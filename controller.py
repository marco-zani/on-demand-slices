# -*- coding: utf-8 -*-

"""
Ryu Tutorial Controller

This controller allows OpenFlow datapaths to act as Ethernet Hubs. Using the
tutorial you should convert this to a layer 2 learning switch.

See the README for more...
"""

from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.lib.dpid import dpid_to_str

from src.common import UDP_IP,UDP_PORT, BUFFER_SIZE
from network import HostDevice
import threading
import socket, dill

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.conf={}
        self.devices = []
        self.pendigMod = []
        self.datapaths = []
        self.dpids = []
        self.modified = False
        p = threading.Thread(target=self.udpClient, args=())
        p.start()

    def udpClient(self):
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        sock.bind(("0.0.0.0", UDP_PORT))
        firstMessage = True

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            if firstMessage:
                firstMessage = False
                self.devices = dill.loads(data)
                print("received devices:")
                for el in self.devices:
                    print(el.hostName, end=" ")
                print("")
            else:
                self.conf = dill.loads(data)
                self.modified = True
                print("new configuration received!")
            
            if data == b"off":
                break
            
            

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        '''
        Handshake: Features Request Response Handler

        Installs a low level (0) flow table modification that pushes packets to
        the controller. This acts as a rule for flow-table misses.
        '''
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.__add_flow(datapath, 0, match, actions, 0)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        '''
        Packet In Event Handler

        Takes packets provided by the OpenFlow packet in event structure and
        floods them to all ports. This is the core functionality of the Ethernet
        Hub.
        '''
        msg = ev.msg
        datapath = msg.datapath
        if datapath not in self.datapaths:
            self.datapaths.append(datapath)
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = datapath.id
        if dpid not in self.dpids:
            self.dpids.append(dpid)
        pkt = packet.Packet(msg.data)
        in_port = msg.match['in_port']

        if self.modified:
            self.wipe_tables()
            self.modified = False

        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        src = eth_pkt.src
        dst = eth_pkt.dst

        
        switchName = "s" + str(dpid)
        srcName = src
        dstName = dst
        for device in self.devices:
            if src in device.MAC:
                srcName = device.hostName
            if dst in device.MAC:
                dstName = device.hostName
        
        out_port,queue_id = self.getPort(srcName,switchName,dstName)
        print("Source: " + str(srcName) + " | Destinazione: " + str(dstName) + " | Out_port: " + str(out_port))
        t = "{...}" if self.conf else "{ }"
        print("dati: " + t)
        if out_port != None:            
            match=parser.OFPMatch(in_port=in_port,eth_dst=dst,eth_src=src)

            data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None

            actions = [parser.OFPActionOutput(out_port)]
            actions.insert(0,parser.OFPActionSetQueue(queue_id))

            self.__add_flow(datapath,1,match,actions,1)

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)

            datapath.send_msg(out)

    def __add_flow(self, datapath, priority, match, actions, table):
        '''
        Install Flow Table Modification

        Takes a set of OpenFlow Actions and a OpenFlow Packet Match and creates
        the corresponding Flow-Mod. This is then installed to a given datapath
        at a given priority.
        '''

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst, table_id=table)
        datapath.send_msg(mod)


    def getPort(self, srcName, switchName, dstName):
        out = None
        queue = None
        
        for slice in self.conf:
            if srcName in slice[0]:
                if switchName in slice[1]:                
                    for port, connDevs in slice[1][switchName]:
                        if dstName in connDevs:
                            out = int(port[0])
                            queue = int(port[1])
                            break
        
        return out,queue
    
    def wipe_tables(self):
        print("Wiping forwarding tables")
        for datapath in self.datapaths:
                self.remove_flows(datapath)

    def remove_flows(self, datapath):
        parser = datapath.ofproto_parser
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath,
                                        empty_match, instructions)
        datapath.send_msg(flow_mod)
    

    def remove_table_flows(self, datapath, match, instructions):
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, 1,
                                                      ofproto.OFPFC_DELETE, 0, 0,
                                                      1,
                                                      ofproto.OFPCML_NO_BUFFER,
                                                      ofproto.OFPP_ANY,
                                                      ofproto.OFPG_ANY, 0,
                                                      match, instructions)
        return flow_mod
