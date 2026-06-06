+++
category = ["Review"]
date = "2026-06-06T17:00:43.319469+00:00"
description = "A difficult paper about a real cloud database's complex and evolving architecture."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "roach1.jpg"
title = "Review: Scalable Leader Leases For Multi Consensus Groups in CockroachDB"
type = "post"
+++

{{% pic src="roach1.jpg" alt="Antique scientific engraving of a wingless cockroach in side profile, its body finely stippled and its abdomen showing distinct segments" / %}}

[Scalable Leader Leases For Multi Consensus Groups in CockroachDB](https://dl.acm.org/doi/abs/10.1145/3788853.3803081), by Ibrahim Kettaneh, Tsvetomira Radeva, Arul Ajmani, Sumeer Bhola, Rebecca Taft (all at Cockroach Labs), and Nathan VanBenschoten (now Turbopuffer). I thought this paper would be easy for me to read, since I just [coauthored a different paper about Raft leases](/leaseguard-raft-leader-leases-done-right/). But I've had a great deal of trouble understanding it, even after a read-through, and Kettaneh's solid presentation at SIGMOD on Tuesday, and a long chat with Claude. I'm writing down my understanding, but I'm not confident. The difficulty is, CRDB is a real system, it's had layers of patches accreted over years, and the paper snapshots it in the midst of migrating from the old protocol to a simpler one. In the meantime the system suffers from the [XKCD Problem](https://xkcd.com/927/): the new protocol coexists with remnants of the old one instead of entirely replacing it. Real systems are palimpsests with adventitious complexity, and this paper describes the situation frankly.

{{< subscribe >}}

{{% pic src="roach4.jpg" alt="Antique scientific engraving of the cockroach Nyctibora sericea seen from above, beside separate detailed drawings of its wings and abdominal segments" / %}}

***

In CockroachDB (CRDB), data is partitioned into ranges. Each range has several replicas, which replicate with Raft. Each node manages many ranges, i.e. it's participating in many Raft consensus groups. A leaseholder is a range's distinguished replica. In the past, all CRDB nodes had liveness records in the same _system range_. Each one proved its liveness by periodically updating its liveness record. Only a node with a recently-updated liveness record could be a leaseholder. That system range with all the liveness records has one leader, who _also_ needs a lease! To recap: normal ranges are protected by leases, which depend on the liveness range, which has its own separate lease protocol. If the system range's leaseholder crashed, none of the normal leases could be renewed until the system range lease expired: single point of failure.

They made a new protocol with fast failover and better scalability, built on CRDB's "Store Liveness" layer. That's a peer-to-peer fabric in which nodes check the health of each other's *stores*. (A store is one disk's worth of storage; a node can host several, but in practice usually one. From now on I'll say "node" and ignore the distinction.) A node "supports" other nodes it thinks are healthy, granting that support irrevocably for an epoch with an expiration. It's roughly all-to-all monitoring---read the paper for the caveats---so I asked about the n-squared cost; Kettaneh said they tested it with thousands of nodes and it's ok.

{{% pic src="roach2.jpg" alt="Antique scientific engraving of two cockroach species, Phoraspis picta and Phoraspis cassidea, with a specimen seen from above beside separate drawings of wings and abdominal segments" / %}}

CRDB's new protocol has a "fortified leader", a leaseholding leader that knows it can't be replaced until a future timestamp. It sends a separate "fortify" request to followers periodically; followers promise not to be candidates or voters until a future timestamp. This interacts with Store Liveness, but there seems to me to be some layering violation and unnecessary complexity. I guess this is a symptom of the architectural history: they started off with a Raft-per-range architecture, accreted _two_ lease protocols, then added the liveness layer, then partly retired Raft's own liveness in favor of it, and this let them retire their old lease protocols. Phew.

An audience member asked at SIGMOD, do leases rely on synced clocks? Kettaneh: They rely on the same 500ms max skew that CRDB assumes in general.

Their past lease protocol allowed gray failures: a stale leaseholder keeps holding its lease but can't make progress, blocking writes indefinitely. Now the lease requires ongoing quorum support from Store Liveness, so losing that support severs the lease; i.e., if a node can't write to its disk anymore, it loses its leases.

This part confused me for a while. The health check is just nodes heartbeating each other over the network---so how does that catch a *disk* problem? The clever bit, which I only understood after Claude searched CRDB's source docs, is that [sending a Store Liveness heartbeat itself requires a disk write](https://github.com/cockroachdb/cockroach/blob/3bb81f36da9de7673f841cc3587b5b1d851b572b/pkg/kv/kvserver/storeliveness/doc.go#L112-L115): "heartbeating requires a disk write, so a store with a stalled disk cannot request support." (CRDB has [an in-process detector](https://www.cockroachlabs.com/docs/stable/wal-failover) that crashes the node if a disk sync stalls for more than 20 seconds, but the liveness fabric reacts faster.)

In our Raft lease protocol, [LeaseGuard](/leaseguard-raft-leader-leases-done-right/), we prevent gray failures more simply: the log is the lease. If a leader can commit log entries, which is pretty much its whole job, then it can also extend its lease. LeaseGuard is luxuriously simple because it's just a research prototype. CockroachDB lives in the real world, and this paper demonstrates the heroic hacking required to improve a real-world system.

{{% pic src="roach3.jpg" alt="Antique scientific engraving of the cockroach Paratropa mexicana seen from above, beside separate drawings of its fore- and hindwings and abdominal segments" / %}}

***

*Cockroach engravings from Carl Brunner von Wattenwyl, [Nouveau système des Blattaires](https://babel.hathitrust.org/cgi/pt?id=uiuo.ark:/13960/t84j0j18p&seq=5) (Vienna: G. Braumüller, 1865), digitized by HathiTrust.*
