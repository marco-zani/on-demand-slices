#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class Topology(Topo):
    def __init__(self):
        Topo.__init__(self)

        hostConf = dict(inNamespace=True)

        type1Link = {"bw":1}
        type2Link = {"bw":5}
        type3Link = {"bw":10}

        for i in range(5):
            sConfig = {"dpid":"%016x" % (i + 1)}
            self.addSwitch("s"+str(i+1), **sConfig)

        for i in range(10):
            self.addHost("h"+str(i+1), **hostConf)

        self.addLink("s1","s2", **type2Link)
        self.addLink("s1","s5", **type2Link)
        self.addLink("s2","s3", **type2Link)
        self.addLink("s3","s4", **type2Link)
        self.addLink("s4","s5", **type2Link)

        
        self.addLink("s1","s3", **type3Link)
        self.addLink("s2","s4", **type3Link)

        self.addLink("s1","h1", **type1Link)
        self.addLink("s1","h2", **type1Link)
        self.addLink("s2","h3", **type1Link)
        self.addLink("s2","h4", **type1Link)
        self.addLink("s3","h5", **type1Link)
        self.addLink("s3","h6", **type1Link)
        self.addLink("s4","h7", **type1Link)
        self.addLink("s4","h8", **type1Link)
        self.addLink("s5","h9", **type1Link)
        self.addLink("s5","h10", **type1Link)

topos = {"topology":(lambda: Topology())}

def listItems(net):
    nodes = list(net.items())
    links = []
    possLinks = []      
    for src in nodes:
        for dst in nodes:
            if (dst[1],src[1]) not in possLinks:
                possLinks.append((src[1], dst[1]))
    
    for src, dst in possLinks:
        link = net.linksBetween(src,dst)
        if link != []:
            for el in link:
                links.append(str(el).replace('-', ' ').replace('< >',' '))

    f = open("links",'w')
    for link in links:
        f.write(link+'\n')
    f.close()

if __name__ == "__main__":
    topo = Topology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink)
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    listItems(net)
    CLI(net)
    net.stop()
