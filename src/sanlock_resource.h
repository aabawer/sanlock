/*
 * Copyright (C) 2010-2011 Red Hat, Inc.  All rights reserved.
 *
 * This copyrighted material is made available to anyone wishing to use,
 * modify, copy, or redistribute it subject to the terms and conditions
 * of the GNU General Public License v.2.
 */

#ifndef __SANLOCK_RESOURCE_H__
#define __SANLOCK_RESOURCE_H__

/*
 * sock > -1, pid is ignored:
 * process creates registered connection and acquires/releases leases on
 * that connection for itself
 *
 * sock == -1, pid is used:
 * process asks daemon to acquire/release leases for another separately
 * registered pid
 */

int sanlock_register(void);

int sanlock_acquire(int sock, int pid, uint32_t flags, int res_count,
		    struct sanlk_resource *res_args[],
		    struct sanlk_options *opt_in);

#define SANLK_REL_ALL 0x1

int sanlock_release(int sock, int pid, uint32_t flags, int res_count,
		    struct sanlk_resource *res_args[]);

int sanlock_inquire(int sock, int pid, uint32_t flags, int *res_count,
		    char **res_state);


/*
 * Functions to convert between string and struct resource formats.
 * All allocate space for returned data that the caller must free.
 */


/*
 * convert from struct sanlk_resource to string with format:
 * <lockspace_name>:<resource_name>:<path>:<offset>[:<path>:<offset>...]:<lver>
 */

int sanlock_res_to_str(struct sanlk_resource *res, char **str_ret);

/*
 * convert to struct sanlk_resource from string with format:
 * <lockspace_name>:<resource_name>:<path>:<offset>[:<path>:<offset>...][:<lver>]
 */

int sanlock_str_to_res(char *str, struct sanlk_resource **res_ret);

/*
 * convert from array of struct sanlk_resource * to state string with format:
 * "RESOURCE1 RESOURCE2 RESOURCE3 ..."
 * RESOURCE format in sanlock_res_to_str() comment
 */

int sanlock_args_to_state(int res_count,
			  struct sanlk_resource *res_args[],
			  char **res_state);

/*
 * convert to array of struct sanlk_resource * from state string with format:
 * "RESOURCE1 RESOURCE2 RESOURCE3 ..."
 * RESOURCE format in sanlock_str_to_res() comment
 */

int sanlock_state_to_args(char *res_state,
			  int *res_count,
			  struct sanlk_resource ***res_args);

/*
 * convert to struct sanlk_lockspace from string with format:
 * <lockspace_name>:<host_id>:<path>:<offset>
 */

int sanlock_str_to_lockspace(char *str, struct sanlk_lockspace *ls);

#endif