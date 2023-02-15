+++
category = ["Review"]
date = "2023-02-14T19:07:52.770271"
description = "A 1994 paper describing how to bring a distributed system to a known state."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "spanning-tree.png"
title = "Review: Distributed Reset"
type = "post"
+++

[Distributed Reset](http://ieeexplore.ieee.org/document/312126/), by Anish Arora and Mohamed Gouda, in IEEE Transactions on Computers, 1994.

Say you have a distributed system, and each node wants the ability to reset all the nodes to some predefined state. "Distributed reset" is a bolt-on protocol you can add to your system. The protocol involves constructing a spanning tree and diffusing the reset message in three waves through the tree.

![](7863159758_e0d81cc6b1_o.jpg)

***

Arora and Gouda's goal is to augment any distributed system with a distributed-reset module, which requires no additional processes or channels, it's just some extra code. The distributed reset brings all nodes to the same "distinguished state". The authors don't want to stop the world while the reset occurs: instead, it's good enough if all nodes pass through the distinguished state, such that the system's subsequent states are *as if* all nodes had been reset simultaneously.

In order to reset all nodes, a message must be able to diffuse from any single node to all the others. To achieve this, nodes continually maintain a **spanning tree**, a DAG that covers all nodes and has a single root node.

The initial state could be *any* directed graph, even one with cycles or isolates:

![](initial-tree.png)

Each node keeps track of which adjacent nodes are alive and figures out who its parent should be, giving precedence to nodes with higher id numbers. How nodes know which peers are alive is an exercise for the reader. The authors assume there's no network partition (big assumption!) and prove that their protocol is self-stabilizing: from any initial state, or after any topology change, the nodes will eventually re-establish a spanning tree with a single root node.

![](spanning-tree.png)

All nodes have a session number, and they somehow all start with the same session number. I've shown the initial session number as "1" here:

![](session-numbers.png)

At any time, some node could decide to start a reset. This decision sets off three waves of messages. First, the reset-initiating node sends a message to its parent. The message keeps bubbling upward to the root:

![](wave-1.png)

Second, the root resets itself to the distinguished state, and increments its session number. It propagates the message down to its children, who also reset themselves and increment their session numbers, and so on to the leaves:

![](wave-2.png)

Third, the leaves send acknowledgements which bubble upward until they reach the root:

![](wave-3.png)

Multiple resets could be in progress at the same time; the purpose of the session numbers is to distinguish them. During normal application logic (that is, aside from the distributed-reset protocol), nodes can only talk with other nodes that have the same session number. Thus if Node A has been reset and Node B hasn't yet, then Node A has session number 1 and Node B has session number 1, and they can't talk until Node B also resets itself. This guarantees that application logic proceeds *as if* all nodes were reset simultaneously.

Interestingly, it's ok for the session number to wrap around when it exceeds some maximum. You could use an 8-byte int, and let the number increment from 255 to 0. The paper says only that the sequence of session numbers must have at least two elements. (From which I infer that the protocol permits only two resets to be in progress.)

That's the gist of the distributed reset protocol. Much of the paper is consumed by meticulous proofs; they're admirable and I ignored them.

![](9061068839_d721f822ef_6k.jpg)

# My evaluation

The paper's spanning-tree algorith is simple and robust. I don't know what advances have been made in the subsequent 30 years for solving the spanning-tree problem, but this seems like a worthy contribution. I wonder if the rest of the paper is obsolete, though.

When is a distributed reset necessary? Arora and Gouda write,

> There are many occasions in which it is desirable for some processes in a distributed system to initiate resets; for example,
> * Reconfiguration: When the system is reconfigured, for instance, by adding processes or channels to it, some process in the system can be signaled to initiate a reset of the system to an appropriate "initial state".
> * Mode Change: The system can be designed to execute in different modes or phases. If this is the case, then changing the current mode of execution can be achieved by resetting the system to an appropriate global state of the next mode.
> * Coordination Loss: When a process observes unexpected behavior from other processes, it recognizes that the coordination between the processes in the system has been lost. In such a situation, coordination can be regained by a reset.
> * Periodic Maintenance: The system can be designed such that a designated process periodically initiates a reset as a precaution, in case the current global state of the system has deviated from the global system invariant.

This seems vague and unconvincing to me. Consider points 3 and 4: I can't picture what the authors mean by "coordination loss" or "periodic maintenance". It sounds like they propose distributed reset as a Band-Aid over buggy software. _Perhaps_ that's a useful application.

Now consider points 1 and 2: "reconfiguration" and "mode change" require all nodes to agree to the new configuration or mode ... in other words, consensus. And if you've solved consensus, you already solved distributed reset. You can just use your consensus protocol to make all nodes agree to the "distinguished state". Furthermore, consensus protocols handle network partitions in predictable ways, whereas the distributed reset protocol was designed with the assumption there isn't a partition; I'm not sure what would happen if there was.

The distributed reset paper was published in 1994, before [Paxos was published in 1998](http://lamport.azurewebsites.net/pubs/pubs.html?from=https://research.microsoft.com/en-us/um/people/lamport/pubs/pubs.html&type=path#lamport-paxos). But Viewstamped Replication had solved consensus in 1988. What does distributed reset offer that isn't a subset of Viewstamped Replication? It's possible that Arora and Gouda weren't aware of VR, or didn't understand its power. They wouldn't be the only researchers to do so. It seems that consensus wasn't a well-distinguished concept among researchers of that era, and it had to be rediscovered a few times before achieving fame. Or perhaps distributed reset can succeed in some situations where no consensus protocol can make progress? This is past the frontiers of my knowledge, if you know then please tell me. 

![](44126679582_6881a6f396_o.jpg)
