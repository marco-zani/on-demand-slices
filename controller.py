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
from commonStaticVariables import UDP_IP,UDP_PORT, BUFFER_SIZE
import threading
import socket, pickle

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.conf={}
        self.macs = {}
        self.pendigMod = []
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
                self.macs = pickle.loads(data)
                for el in self.macs:
                    print(el)
            else:
                self.conf = pickle.loads(data)
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
        print("Handshake taken place with {}".format(dpid_to_str(datapath.id)))
        self.__add_flow(datapath, 0, match, actions)


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
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = datapath.id
        if dpid not in self.dpids:
            self.dpids.append(dpid)
            print("Registered switches:", self.dpids)
        pkt = packet.Packet(msg.data)
        in_port = msg.match['in_port']

        if self.modified:
            self.pendigMod = self.dpids
            self.modified = False

        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        src = eth_pkt.src
        dst = eth_pkt.dst

        
        switchName = "s" + str(dpid)
        srcName = src
        dstName = dst
        if src in self.macs:
            srcName = self.macs[src]
        if dst in self.macs:
            dstName = self.macs[src]
        
        print("Source: " + str(srcName) + " | Destinazione: " + str(dstName) + " | In_port: " + str(in_port) + " | Dpid: " + str(switchName))

        out_port = self.getPort(in_port,switchName,dst)
        if out_port != None:
            if len(self.pendigMod) != 0 and dpid not in self.pendigMod:
                print("before:", self.pendigMod)
                if dpid in self.pendigMod:
                    self.pendigMod.remove(dpid)
                    print("after:", self.pendigMod)
                    match = parser.OFPMatch()
                    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
                    self.__add_flow(datapath,1,match,actions)
            
            match=parser.OFPMatch(in_port=in_port,eth_dst=dst,eth_src=src)

            data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
            #actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

            actions = [parser.OFPActionOutput(out_port)]
            self.__add_flow(datapath,1,match,actions)

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)

            datapath.send_msg(out)

    def __add_flow(self, datapath, priority, match, actions):
        '''
        Install Flow Table Modification

        Takes a set of OpenFlow Actions and a OpenFlow Packet Match and creates
        the corresponding Flow-Mod. This is then installed to a given datapath
        at a given priority.
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        self.logger.info("Flow-Mod written to {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)



    def getPort(self, in_port, switchName, dst):
        out = None
        
        if dst in self.macs:
            dstName = self.macs[dst]
        else:
            return out
        
        if switchName in self.conf:
            for port, connDevs in self.conf[switchName]:
                if dstName in connDevs:
                    out = int(port)
                    break
            
        print("Get port output: " + str(out) )
        return out



        