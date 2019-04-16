# Copyright 2010-2011 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2.

all:
	python$(PY_VERSION) setup.py build $(BUILDARGS)

install:
	python$(PY_VERSION) setup.py install --root=$(DESTDIR)

clean:
	rm -rf build

