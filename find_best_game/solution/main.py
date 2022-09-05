from scapy.all import *
from scapy.layers.tls.record import TLS
from scapy.layers.tls.cert import PrivKey
from scapy.layers.tls.session import TLSSession

load_layer('tls')
pcapfile = "../best_game.pcap"
keyfile = "../server.key"

privKey = PrivKey(keyfile)
session = TLSSession(server_rsa_key=privKey)
taste = sniff(offline=pcapfile, session=session)

for pkt in taste:
    if pkt.haslayer(TLS): pkt.show()
