#ifndef __PAXOS_LEASE_H__
#define __PAXOS_LEASE_H__

uint32_t leader_checksum(struct leader_record *lr);
int majority_disks(struct token *token, int num);
int paxos_lease_leader_read(struct token *token, struct leader_record *leader_ret);
int paxos_lease_acquire(struct token *token, int force,
		        struct leader_record *leader_ret,
		        uint64_t reacquire_lver);
int paxos_lease_migrate(struct token *token,
                        struct leader_record *leader_last,
                        struct leader_record *leader_ret,
                        uint64_t target_host_id);
int paxos_lease_release(struct token *token,
		        struct leader_record *leader_last,
		        struct leader_record *leader_ret);
int paxos_lease_init(struct token *token, int num_hosts, int max_hosts);

#endif
