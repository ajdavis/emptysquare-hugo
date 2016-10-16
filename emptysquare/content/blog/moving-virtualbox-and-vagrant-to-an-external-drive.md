+++
type = "post"
title = "Moving VirtualBox and Vagrant to an external drive"
date = "2012-05-03T22:21:16"
description = "When I joined 10gen they gave me a MacBook Pro with an SSD drive. This is wonderful, mainly because it loads StarCraft II really fast. An SSD is like my studio apartment on the Lower East Side: low latency, but a bit cramped. (My apartment is [ ... ]"
categories = ["Programming"]
tags = []
enable_lightbox = false
thumbnail = "hippie.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="hippie.png" title="Vagrant" /></p>
<p>When I joined 10gen they gave me a MacBook Pro with an SSD drive. This
is wonderful, mainly because it loads StarCraft II really fast. An SSD
is like my studio apartment on the Lower East Side: low latency, but a
bit cramped. (My apartment is low-latency because it's a 10-minute walk
from work. This is not a strained analogy.)</p>
<p>Lately I've needed to spin up a bunch of virtual machines with
<a href="https://www.virtualbox.org/">VirtualBox</a> and
<a href="http://vagrantup.com/">Vagrant</a> for testing <a href="/blog/requests-in-python-and-mongodb/">our changes to
PyMongo</a> under every conceivable
OS, and there's no room for them on my SSD. Even if they run heinously
slow on a USB drive, they can't stay in my apartment. Here's how I moved
them to an external hard drive:</p>
<ul>
<li>Move \~/.vagrant.d to the external drive. I renamed it vagrant_home
    so I'd be able to see it without <code>ls -a</code>.</li>
<li>Set VAGRANT_HOME to "/path/to/drive/vagrant_home" in
    \~/.bash_profile.</li>
<li>Open the VirtualBox app, open Preferences, and set its Default
    Machine Folder to "/path/to/drive/VirtualBox VMs".</li>
<li>Close VirtualBox.</li>
<li>Move your "VirtualBox VMs" folder to the drive.</li>
<li>Reopen VirtualBox. You'll see your VMs are listed as "inaccessible".
    Remove them from the list.</li>
<li>For each VM in your "VirtualBox VMs" folder on the external drive,
    browse to its folder in Finder and double-click the .vbox file to
    restore it to the VirtualBox Manager. (Is there an easier method
    than this?)</li>
<li>Finally, move any existing Vagrant directories you've made with
    <code>vagrant init</code> (these are the directories with a Vagrantfile in
    each) to the external drive. Since these directories only store
    metadata you could leave them on your main drive, but it's nice to
    keep everything together so you could fairly easily plug the whole
    drive into another machine and start your VMs from there.</li>
</ul>
<p>Good to go. This has freed up a ton of space on my main drive, and the
speed penalty has not been very bad.</p>
    