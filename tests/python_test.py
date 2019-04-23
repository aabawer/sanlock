"""
Test sanlock python binding with sanlock daemon.
"""
from __future__ import absolute_import

import errno
import io
import struct
import time

import pytest

import sanlock

from . import constants
from . import util

# Largest file size on ext4 is 16TiB, and on xfs 500 TiB. Use 1 TiB as it is
# large enough to test large offsets, and less likely to fail on developer
# machine or CI slave.
# See https://access.redhat.com/articles/rhel-limits
LARGE_FILE_SIZE = 1024**4

LOCKSPACE_SIZE = 1024**2
MIN_RES_SIZE = 1024**2


@pytest.mark.parametrize("size,offset", [
    # Smallest offset.
    (LOCKSPACE_SIZE, 0),
    # Large offset.
    (LARGE_FILE_SIZE, LARGE_FILE_SIZE - LOCKSPACE_SIZE),
])
@pytest.mark.parametrize("path_encoding", [
    None,
    'utf-8',
    'ascii',
])
def test_write_lockspace(tmpdir, sanlock_daemon, size, offset, path_encoding):
    path = util.generate_path(tmpdir, "lockspace", path_encoding)
    print("path=",path)
    util.create_file(path, size)

    sanlock.write_lockspace("name", path, offset=offset, iotimeout=1)

    ls = sanlock.read_lockspace(path, offset=offset)
    assert ls == {"iotimeout": 1, "lockspace": b"name"}

    acquired = sanlock.inq_lockspace(
        "name", 1, path, offset=offset, wait=False)
    assert acquired is False

    with io.open(path, "rb") as f:
        f.seek(offset)
        magic, = struct.unpack("< I", f.read(4))
        assert magic == constants.DELTA_DISK_MAGIC

        # TODO: check more stuff here...

    util.check_guard(path, size)


@pytest.mark.parametrize("size,offset", [
    # Smallest offset.
    (MIN_RES_SIZE, 0),
    # Large offset.
    (LARGE_FILE_SIZE, LARGE_FILE_SIZE - MIN_RES_SIZE),
])
@pytest.mark.parametrize("path_encoding", [
    None,
    'utf-8',
    'ascii',
])
def test_write_resource(tmpdir, sanlock_daemon, size, offset, path_encoding):
    path = util.generate_path(tmpdir, "resources", path_encoding)
    util.create_file(path, size)
    disks = [(path, offset)]

    sanlock.write_resource("ls_name", "res_name", disks)

    res = sanlock.read_resource(path, offset=offset)
    assert res == {
        "lockspace": b"ls_name",
        "resource": b"res_name",
        "version": 0
    }

    owners = sanlock.read_resource_owners("ls_name", "res_name", disks)
    assert owners == []

    with io.open(path, "rb") as f:
        f.seek(offset)
        magic, = struct.unpack("< I", f.read(4))
        assert magic == constants.PAXOS_DISK_MAGIC

        # TODO: check more stuff here...

    util.check_guard(path, size)


@pytest.mark.parametrize("size,offset", [
    # Smallest offset.
    (MIN_RES_SIZE, 0),
    # Large offset.
    (LARGE_FILE_SIZE, LARGE_FILE_SIZE - MIN_RES_SIZE),
])
@pytest.mark.parametrize("path_encoding", [
    None,
    'utf-8',
    'ascii',
])
def test_add_rem_lockspace(tmpdir, sanlock_daemon, size, offset, path_encoding):
    path = util.generate_path(tmpdir, "ls_name", path_encoding)
    util.create_file(path, size)

    sanlock.write_lockspace("ls_name", path, offset=offset, iotimeout=1)

    # Since the lockspace is not acquired, we exepect to get False.
    acquired = sanlock.inq_lockspace(
        "ls_name", 1, path, offset=offset, wait=False)
    assert acquired is False

    sanlock.add_lockspace("ls_name", 1, path, offset=offset, iotimeout=1)

    # Once the lockspace is acquired, we exepect to get True.
    acquired = sanlock.inq_lockspace(
        "ls_name", 1, path, offset=offset, wait=False)
    assert acquired is True

    sanlock.rem_lockspace("ls_name", 1, path, offset=offset)

    # Once the lockspace is released, we exepect to get False.
    acquired = sanlock.inq_lockspace(
        "ls_name", 1, path, offset=offset, wait=False)
    assert acquired is False

@pytest.mark.parametrize("path_encoding", [
    None,
    'utf-8',
    'ascii',
])
def test_add_rem_lockspace_async(tmpdir, sanlock_daemon, path_encoding):
    path = util.generate_path(tmpdir, "ls_name", path_encoding)
    util.create_file(path, 1024**2)

    sanlock.write_lockspace("ls_name", path, iotimeout=1)
    acquired = sanlock.inq_lockspace("ls_name", 1, path, wait=False)
    assert acquired is False

    # This will take 3 seconds.
    sanlock.add_lockspace("ls_name", 1, path, iotimeout=1, **{"async": True})

    # While the lockspace is being aquired, we expect to get None.
    time.sleep(1)
    acquired = sanlock.inq_lockspace("ls_name", 1, path, wait=False)
    assert acquired is None

    # Once the lockspace is acquired, we exepect to get True.
    acquired = sanlock.inq_lockspace("ls_name", 1, path, wait=True)
    assert acquired is True

    # This will take about 3 seconds.
    sanlock.rem_lockspace("ls_name", 1, path, **{"async": True})

    # Wait until the lockspace change state from True to None.
    while sanlock.inq_lockspace("ls_name", 1, path, wait=False):
        time.sleep(1)

    # While the lockspace is being released, we expect to get None.
    acquired = sanlock.inq_lockspace("ls_name", 1, path, wait=False)
    assert acquired is None

    # Once the lockspace was released, we expect to get False.
    acquired = sanlock.inq_lockspace("ls_name", 1, path, wait=True)
    assert acquired is False


@pytest.mark.parametrize("size,offset", [
    # Smallest offset.
    (MIN_RES_SIZE, 0),
    # Large offset.
    (LARGE_FILE_SIZE, LARGE_FILE_SIZE - MIN_RES_SIZE),
])
@pytest.mark.parametrize("path_encoding", [
    None,
    'utf-8',
    'ascii',
])
def test_acquire_release_resource(tmpdir, sanlock_daemon, size, offset, path_encoding):
    ls_path = util.generate_path(tmpdir, "ls_name", path_encoding)
    util.create_file(ls_path, size)

    res_path = util.generate_path(tmpdir, "res_name", path_encoding)
    util.create_file(res_path, size)

    sanlock.write_lockspace("ls_name", ls_path, offset=offset, iotimeout=1)
    sanlock.add_lockspace("ls_name", 1, ls_path, offset=offset, iotimeout=1)

    # Host status is not available until the first renewal.
    with pytest.raises(sanlock.SanlockException) as e:
        sanlock.get_hosts("ls_name", 1)
    assert e.value.errno == errno.EAGAIN

    time.sleep(1)
    host = sanlock.get_hosts("ls_name", 1)[0]
    assert host["flags"] == sanlock.HOST_LIVE

    disks = [(res_path, offset)]
    sanlock.write_resource("ls_name", "res_name", disks)

    res = sanlock.read_resource(res_path, offset=offset)
    assert res == {
        "lockspace": b"ls_name",
        "resource": b"res_name",
        "version": 0
    }

    owners = sanlock.read_resource_owners("ls_name", "res_name", disks)
    assert owners == []

    fd = sanlock.register()
    sanlock.acquire("ls_name", "res_name", disks, slkfd=fd)

    res = sanlock.read_resource(res_path, offset=offset)
    assert res == {
        "lockspace": b"ls_name",
        "resource": b"res_name",
        "version": 1
    }

    owner = sanlock.read_resource_owners("ls_name", "res_name", disks)[0]

    assert owner["host_id"] == 1
    assert owner["flags"] == 0
    assert owner["generation"] == 1
    assert owner["io_timeout"] == 0  # Why 0?
    # TODO: check timestamp.

    host = sanlock.get_hosts("ls_name", 1)[0]
    assert host["flags"] == sanlock.HOST_LIVE
    assert host["generation"] == owner["generation"]

    sanlock.release("ls_name", "res_name", disks, slkfd=fd)

    res = sanlock.read_resource(res_path, offset=offset)
    assert res == {
        "lockspace": b"ls_name",
        "resource": b"res_name",
        "version": 1
    }

    owners = sanlock.read_resource_owners("ls_name", "res_name", disks)
    assert owners == []
