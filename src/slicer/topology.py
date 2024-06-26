import src.slicer.floydWarshall as fw

class TopologyStruct:
    def __init__(self) -> None:
        self.devices = {}
        self.activeConfiguration = []
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
    
    def getPort(self, src, dst):
        for port, device in self.devices[src]:
            if device == dst:
                return port
        return None
            
    def convertProfileInConfiguration(self, prf):
        conf = []
        max_perc = []
        for slice in prf.slices:   
            hosts = []
            max_perc.append((slice['maxBandwidth'])/10)
            for dev in slice['devices']:
                if dev[0] == 'h':
                    hosts.append(dev)
            n = len(slice['devices'])
            adjMatrix = fw.initMatrix(n,slice['devices'],self.devices)
            nextHopMatrix = fw.compute_next_hop(adjMatrix)
            shrinkedTable = fw.shrinkTable(nextHopMatrix, slice['devices'])
            forwardingTable =  fw.convertToDict(shrinkedTable, slice['devices'])
            portsTable = self.convertPorts(forwardingTable)
            conf.append((hosts, fw.extractSwitches(portsTable)))
        
        fw.add_max_bandwidth(conf, max_perc)
        return conf
    
    def convertPorts(self, table):
        out = {}
        for key in table:
            for nextHop, reachableHosts in table[key]:
                port = self.getPort(key,nextHop)
                if key not in out:
                    out.update({key:[((port,10), reachableHosts)]})
                else:
                    out[key].append(((port,10),reachableHosts))
        return out