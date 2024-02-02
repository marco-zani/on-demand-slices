
import json
from time import sleep
from os.path import exists
from os import remove as deleteFile
import floydWarshall as fw

def loadProfiles():
        with open('profiles.json', 'r') as file:
            data = json.load(file)
        return data        

def uploadData(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def saveData(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

class ConfEntry:
    def __init__(self):
        self.id = None
        self.ports = []

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
        n = len(prf)
        adjMatrix = fw.initMatrix(n,prf,self.devices)
        nextHopMatrix = fw.compute_next_hop(adjMatrix)
        shrinkedTable = fw.shrinkTable(nextHopMatrix, prf)
        forwardingTable =  fw.convertToDict(shrinkedTable, prf)
        portsTable = self.convertPorts(forwardingTable)
        conf = fw.extractSwitches(portsTable)
        
        for el in conf:
            print(el+":"+str(conf[el]))
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


    
class Slicer:
    def __init__(self, send) -> None:
        self.send = send
        #Variabile globale per slice attiva, valore default
        self.sliceActive = 1
        self.topology = TopologyStruct()
        pass

    def acceptCommand(self):
        choice = input("\nSelect function:\n1 - listNetElements\n2 - listSlicingProfiles\n3 - listActiveProfiles\n4 - createNewProfile\n5 - toggleProfile\n0 - exit\n")
        if choice == "0":
            return False
        elif choice == "1":
            self.listNetElements()
            return True
        elif choice == "2":
            self.listSlicingProfiles()
            return True
        elif choice == "3":
            self.listActiveProfiles()
            return True
        elif choice == "4":
            self.createNewProfile()
            return True
        elif choice == "5":
            self.toggleProfile()           
            return True

    def listNetElements(self):
        print("\nListing default network")
        
        links = self.topology.getLinks()
        linksStr = []
        hostStr = []
        for src,dst in links:
            linksStr.append(src.name+"-"+src.port+" -> "+dst.port+"-"+dst.name)
            for host in [src,dst]:
                if host.name not in hostStr:
                    hostStr.append(host.name)
        print("Hosts:")
        for el in hostStr:
            print(el)
        print("\nLinks:")
        for el in linksStr:
            print(el)

    def listSlicingProfiles(self):
        print("\nListing all profiles")

        data = loadProfiles()
        #Ciclo while che stampa ogni elemento del file
        for el in data:
            print(el)
        

    def listActiveProfiles(self):
        print("\nListing active profiles")
        
        data = loadProfiles()

        #Stampa dati relativi alla variabile globale selezionata
        print(json.dumps(data[self.sliceActive-1],indent=4))


    def createNewProfile():
        # Carica i dati dal file
        file_path = 'profiles.json'
        dati_originali = uploadData(file_path)
        
        # Get id attuale massimo
        max_id = max(entry[next(iter(entry))]['id'] for entry in dati_originali)
        next_id = max_id + 1

        # Aggiungi una nuova slice
        nuova_slice_name = input("Inserisci il nome della nuova slice: ")

        # Crea la nuova slice
        nuova_slice = {
            nuova_slice_name: {
                "id": next_id,
                "links": []
            }
        }

        # Inserimento links
        while True:
            source_host = input("Inserisci l'host sorgente: ")
            target_host = input("Inserisci l'host di destinazione: ")

            nuova_slice[nuova_slice_name]['links'].append({
                "source": source_host,
                "target": target_host
            })
            risposta = input("Vuoi inserire un altro collegamento? (s per si, n per uscire): ")
            if risposta.lower() == 'n':
                break

        dati_originali.append(nuova_slice)

        # Salva i dati aggiornati nel file
        saveData(dati_originali, file_path)

        print("Aggiunta nuova slice con id -> " + str(next_id))
        
    def toggleProfile(self):
        profileId = input("\nQuale slice vuoi attivare?:")
        self.sliceActive = int(profileId)
        print("\nActivating profile n." + str(self.sliceActive))
        temp = loadProfiles()
        prf = []
        for el in temp:
            for subEl in el.values():
                if subEl["id"] == self.sliceActive:
                    prf = subEl["devices"]
                    break
            if prf != []:
                break
        self.topology.activeConfiguration = self.topology.convertProfileInConfiguration(prf)
        self.send(self.topology.activeConfiguration)

        
    def importTopology(self):
        fileName = 'links'
        while not exists(fileName):
            sleep(3)
        f = open(fileName)
        for el in f:
            el = el.replace('\n','')
            t = el.split(' ')
            self.topology.addLink(t[0],t[1].replace('eth',''),t[2],t[3].replace('eth',''))
        f.close()
        deleteFile(fileName)

        for el in self.topology.getLinks():
            print(el)


    def start(self):
        self.importTopology()
        while(self.acceptCommand()):
            sleep(0.5)


