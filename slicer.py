
import json
from time import sleep
from os.path import exists
from os import remove as deleteFile
from topology import TopologyStruct
import socket, pickle
from common import UDP_IP, UDP_PORT

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
        return out

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