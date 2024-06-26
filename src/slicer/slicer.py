
import json
from time import sleep
from os.path import exists
from os import remove as deleteFile
from src.slicer.topology import TopologyStruct
import socket, dill
from src.common import UDP_IP, UDP_PORT

def uploadData(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def saveData(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

class Slice():
    def __init__(self, devices, maxBandwidth) -> None:
        self.devices = devices
        self.maxBandwidth = maxBandwidth

class Profile:
    def __init__(self,id, name, slices):
        self.id = id
        self.name = name
        self.slices = slices
    
class Slicer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Variabile globale per slice attiva, valore default
        self.sliceActive = 0

        self.profiles = self.getProfiles()
        
        self.topology = TopologyStruct()       
        self.importTopology()

        self.sendDevices()
        pass

    def getProfiles(self):
        out = []

        with open('data/profiles.json', 'r') as file:
            data = json.load(file)

        for el in data:
            t = Profile(el["id"],el["name"],el["slices"])
            out.append(t)
        return out
        
    def sendUDP(self, data):
        self.sock.sendto(data, ("0.0.0.0", UDP_PORT))

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

    def sendDevices(self):
        fileName = 'devices'
        while not exists(fileName):
            sleep(3)
        f = open(fileName, "rb")
        msg = f.read()
        f.close()
        deleteFile(fileName)

        self.sendUDP(msg)

    def toggleProfile(self, id):
        prevId = self.sliceActive
        self.sliceActive = int(id)
        self.topology.activeConfiguration = self.topology.convertProfileInConfiguration(self.profiles[id])
        print("Switched from", self.profiles[prevId].name, "to", self.profiles[id].name+": { ... }")
        data = dill.dumps(self.topology.activeConfiguration)
        self.sendUDP(data)
