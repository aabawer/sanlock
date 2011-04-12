/*
 * Copyright (C) 2010-2011 Red Hat, Inc.  All rights reserved.
 *
 * This copyrighted material is made available to anyone wishing to use,
 * modify, copy, or redistribute it subject to the terms and conditions
 * of the GNU General Public License v.2.
 */

#ifndef __DELTA_LEASE_H__
#define __DELTA_LEASE_H__

int delta_lease_leader_read(struct sync_disk *disk, char *space_name,
			    uint64_t host_id, struct leader_record *leader_ret);
int delta_lease_acquire(struct space *sp, struct sync_disk *disk, char *space_name,
			uint64_t our_host_id, uint64_t host_id,
			struct leader_record *leader_ret);
int delta_lease_renew(struct space *sp, struct sync_disk *disk, char *space_name,
		      uint64_t our_host_id, uint64_t host_id,
		      struct leader_record *leader_ret);
int delta_lease_release(struct space *sp, struct sync_disk *disk, char *space_name,
			uint64_t host_id,
			struct leader_record *leader_last,
			struct leader_record *leader_ret);
int delta_lease_init(struct sync_disk *disk, char *space_name, int max_hosts);

#endif