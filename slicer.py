
import json
from time import sleep
from os.path import exists
from os import remove as deleteFile
from topology import TopologyStruct
import socket, pickle
from commonStaticVariables import UDP_IP, UDP_PORT

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

class Profile:
    def __init__(self,id, name, devices):
        self.id = id
        self.name = name
        self.devices = devices
    
class Slicer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Variabile globale per slice attiva, valore default
        self.sliceActive = 1
        self.topology = TopologyStruct()
        self.profiles = self.getProfiles()
        pass

    def getProfiles(self):
        out = []

        data = loadProfiles()
        #Ciclo while che stampa ogni elemento del file


        for el in data:
            t = Profile(el["id"],el["name"],el["devices"])
            out.append(t)
        print("Done")
        return out

    def acceptCommand(self):
        choice = input("\nSelect function:\n1 - listNetElements\n2 - listSlicingProfiles\n3 - listActiveProfiles\n4 - createNewProfile\n5 - toggleProfile\n0 - exit\n")
        if choice == "0":
            self.sendUDP(b"off")
            self.sock.close()
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
        
    def sendUDP(self, data):
        self.sock.sendto(data, ("0.0.0.0", UDP_PORT))

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
        data = pickle.dumps(self.topology.activeConfiguration)
        self.sendUDP(data)

        
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
        #deleteFile(fileName)

    def sendMACs(self):
        macs = {}
        fileName = 'macs'
        while not exists(fileName):
            sleep(3)
        f = open(fileName)
        for el in f:
            el = el.replace('\n','')
            t = el.split('-')
            macs.update({t[1]:t[0]})
        f.close()
        #deleteFile(fileName)

        msg = pickle.dumps(macs)
        self.sendUDP(msg)


    def start(self):
        self.importTopology()
        self.sendMACs()
        while(self.acceptCommand()):
            sleep(0.5)