= Dockerized open-vmdk tools =
open-vmdk tools from https://github.com/vmware/open-vmdk can create an OVA file from VMDK and an OVF template.
However, it requires Linux to run.

This dockerized version allows you to use vmware's utility on any host that can run Python 3+ and docker.

= Usage =

== Requirements ==
* Docker
* Python 3+
* Shell
* A VMDK image
* An OVF template (you can use the included one, if you like)

== Example ==

1. Clone the repository and cd to it
2. ./build.sh
3. ./run.py -n my-virtual-machine -t ./template-hw14-bios.ovf -o /tmp -i /tmp/testsensor-disk1.vmdk
4. You should have /tmp/my-virtual-machine.ova once the tool completes.
