from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController, Node
from mininet.cli import CLI
from mininet.link import TCLink
import os
import dill


class HostDevice:
    def __init__(self, hostName, MAC, IP) -> None:
        self.hostName = hostName
        self.MAC = MAC
        self.IP = IP


class Topology(Topo):
    def __init__(self):
        Topo.__init__(self)

        hostConf = dict(inNamespace=True)

        for i in range(5):
            sConfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s" + str(i + 1), **sConfig)

        for i in range(10):
            self.addHost("h" + str(i + 1), **hostConf)

        self.addLink("s1", "s2")
        self.addLink("s1", "s5")
        self.addLink("s2", "s3")
        self.addLink("s3", "s4")
        self.addLink("s4", "s5")

        self.addLink("s1", "s3")
        self.addLink("s2", "s4")

        self.addLink("s1", "h1")
        self.addLink("s1", "h2")
        self.addLink("s2", "h3")
        self.addLink("s2", "h4")
        self.addLink("s3", "h5")
        self.addLink("s3", "h6")
        self.addLink("s4", "h7")
        self.addLink("s4", "h8")
        self.addLink("s5", "h9")
        self.addLink("s5", "h10")


topos = {"topology": (lambda: Topology())}


def qos(switches):
    
    for s in switches:
        
        queuecmd = "sudo ovs-vsctl "
        queuecmd += (
            "set port "
            + s
            + " qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000000 "
        )

        for i in range(1,11):
            i = str(i)
            queuecmd += "queues:" + i + "=@q" + i + " "

        for i in range(1,11):
            i = str(i)
            queuecmd += (
                "-- --id=@q" + i + " create queue other-config:max-rate=" + i + "00000000 "
            )
        os.popen(queuecmd)


def listItems(net):
    nodes = list(net.items())
    links = []
    possLinks = []
    for src in nodes:
        for dst in nodes:
            if (dst[1], src[1]) not in possLinks:
                possLinks.append((src[1], dst[1]))

    for src, dst in possLinks:
        link = net.linksBetween(src, dst)
        if link != []:
            for el in link:
                links.append(str(el).replace("-", " ").replace("< >", " "))

    switches = []
    for link in links:
        t = str(link).split(" ")
        if t[0][0] == "s" and t[2][0] == "s":
            switches.append(t[0] + "-" + t[1])
            switches.append(t[2] + "-" + t[3])

    qos(switches)

    with open("links", "w") as f:
        for link in links:
            f.write(link + "\n")
    


def listIp(net):
    devs = net.items()
    conv = list()
    for name, _ in devs:
        if name[0] != "c" and name[0] != "s":
            conv.append(
                HostDevice(
                    name, str(Node.MAC(net.get(name))), str(Node.IP(net.get(name)))
                )
            )

    with open("devices", "wb") as f:
        f.write(dill.dumps(conv))
    


if __name__ == "__main__":
    topo = Topology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    listItems(net)
    listIp(net)
    CLI(net)
    net.stop()
