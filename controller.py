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
import multiprocessing as mp 
from multiprocessing import shared_memory as sm
import socket, pickle

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        if __name__ == "__main__":
            super(Controller, self).__init__(*args, **kwargs)
            self.manager = mp.Manager()
            self.conf = self.manager.dict()
            self.macs = self.manager.dict()
            p = mp.Process(target=self.udpClient, args=())
            p.start()

    def udpClient(self):
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        firstMessage = True

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            if firstMessage:
                firstMessage = False
                self.macs = pickle.loads(data)
            print("received message: " + str(data))
            if data == b"off":
                self.manager.shutdown()
                break
            self.conf = pickle.loads(data)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        """
        Handshake: Features Request Response Handler

        Installs a low level (0) flow table modification that pushes packets to
        the controller. This acts as a rule for flow-table misses.
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        print("Handshake taken place with {}".format(dpid_to_str(datapath.id)))
        self.__add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Packet In Event Handler

        Takes packets provided by the OpenFlow packet in event structure and
        floods them to all ports. This is the core functionality of the Ethernet
        Hub.
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = datapath.id
        pkt = packet.Packet(msg.data)
        in_port = msg.match["in_port"]

        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        src = eth_pkt.src
        dst = eth_pkt.dst
        print("Destinazione: " + str(dst))
        out_port = self.getPort(in_port, dpid, dst)

        match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)

        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        # actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        actions = [parser.OFPActionOutput(out_port)]
        self.__add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )

        datapath.send_msg(out)

    def __add_flow(self, datapath, priority, match, actions):
        """
        Install Flow Table Modification

        Takes a set of OpenFlow Actions and a OpenFlow Packet Match and creates
        the corresponding Flow-Mod. This is then installed to a given datapath
        at a given priority.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        self.logger.info("Flow-Mod written to {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)



    def getPort(self, in_port, dpid, dst):
        switchName = "s" + str(dpid)
        dstName = self.macs[dst]

        for port, connDevs in self.conf[switchName]:
            if dstName in connDevs:
                return port
            
        return None



        