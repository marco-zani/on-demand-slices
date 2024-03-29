import floydWarshall as fw

class TopologyStruct:
    def __init__(self) -> None:
        self.devices = {}
        self.activeConfiguration = None
        pass

    def addDevice(self, name):
        if name not in self.devices.keys():
            self.devices.update({name:[]}) 

    def addLink(self, srcName, srcPort, dstName, dstPort):
        self.addDevice(srcName)
        self.addDevice(dstName)

        if (srcPort, dstName) not in self.devices[srcName]:
            self.devices[srcName].append((srcPort,dstName))
        if (dstPort, srcName) not in self.devices[dstName]:
            self.devices[dstName].append((dstPort,srcName))    

    def getLinks(self):
        out = []
        for dev in self.devices:
            for port, endDev in self.devices[dev]:
                out.append(dev + " -eth" + port + "-> " + endDev)
        return out
    
    def getPort(self, src, dst):
        for port, device in self.devices[src]:
            if device == dst:
                return port
        return None
            
    def convertProfileInConfiguration(self, prf):
        conf = []
        for slice in prf.slices:   
            hosts = []
            for dev in slice:
                if dev[0] == 'h':
                    hosts.append(dev)
            n = len(slice)
            adjMatrix = fw.initMatrix(n,slice,self.devices)
            nextHopMatrix = fw.compute_next_hop(adjMatrix)
            shrinkedTable = fw.shrinkTable(nextHopMatrix, slice)
            forwardingTable =  fw.convertToDict(shrinkedTable, slice)
            portsTable = self.convertPorts(forwardingTable)
            conf.append((hosts, fw.extractSwitches(portsTable)))

        return conf
    
    def convertPorts(self, table):
        out = {}
        for key in table:
            for nextHop, reachableHosts in table[key]:
                port = self.getPort(key,nextHop)
                if key not in out:
                    out.update({key:[(port, reachableHosts)]})
                else:
                    out[key].append((port,reachableHosts))
        return out