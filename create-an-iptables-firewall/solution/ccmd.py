from cmd import Cmd
from link import Link
from canvas import *
from os import system
import subprocess

class CCMD(Cmd):
    def __init__(self, name="") -> None:
        super().__init__(completekey='tab', stdin=None, stdout=None)
        super.__setattr__(self, "prompt", f'{name}> ')
        self.name = name
        self.peerIndex = 0
        self.nslist = {}
        self.lnklist = {}
        self.avalnklist = {}
        self.dummy_ns = Namespace('1')
        self.app = GUI(self.dummy_ns)
        for ns in subprocess.Popen(f'ip netns list', shell=True, stdout=subprocess.PIPE)\
                                .stdout.read().decode().split("\n"):
            if ns == '': continue
            self.nslist[ns] = None
        for ns in subprocess.Popen(f'ip netns list', shell=True, stdout=subprocess.PIPE)\
                                .stdout.read().decode().split("\n"):
            if ns == '': continue
            self.nslist[ns] = None
    
    def postloop(self) -> None:
        self.app.update()

    def default(self, line):
        """Runs unimplemented functions in superuser shell. Use --force-execute for no confirm."""
        if "--force-execute" in line:
            pass
        elif input("Do you want to continue with non implemented function in superuser mode? y/N: ") in ('y','Y'):
            pass
        else:
            return
        system(line.replace("--force-execute",""))

    def do_clear(self, arg):
        """Clears screen."""
        system("clear")

    def do_exit(self, arg):
        """Clears namespaces and exits."""
        subprocess.Popen(f'ip -all netns delete', shell=True)
        self.do_lnk("-d all")
        print("Namespaces and links are cleared")
        print("OUT...")
        return True       

    def do_ns(self, arg):
        """
        -c, --change NAMESPACE                      changes global to namespace
        -l, --list                                  lists available namespaces
        -a, --add NAMESPACE;[NAMESPACE;...]             add one or more namespace 
                                                     with seperated by ';'
        -d, --del [all] | NAMESPACE[;NAMESPACE;...]     delete one or more namespace with 
                                                     seperated by ';' or delete all
        """
        gl_args = arg.split(" ")
        if gl_args[0] in ("-c", "--change"):
            if not len(gl_args) > 1:
                print("At least one argument is needed.")
            else:
                if gl_args[1] in self.nslist:
                    namespace = self.nslist[gl_args[1]]
                    namespace.cmdloop()
                else:
                    print(f'{gl_args[1]} is not available.')

        elif gl_args[0] in ("-l", "--list"):
            for k in self.nslist:
                print(k)

        elif gl_args[0] in ("-a", "--add"):
            if not len(gl_args) > 1:
                print("At least one argument is needed.")
            else:
                for n in gl_args[1].split(';'):
                    if not n in ("all","1"):
                        subprocess.Popen(f'ip netns add {n}', shell=True)
                        self.nslist[n] = Namespace(n)
                        self.app.ns[n] = GUI_Ns(self.app, (0,0), self.nslist[n])
                    else:
                        print(f'{n} is invalid namespace name. Passed.')
                        
        
        elif gl_args[0] in ("-d", "--del"):
            if not len(gl_args) > 1:
                print("At least one argument is needed.")
            else:
                if gl_args[1] == "all":
                    subprocess.Popen(f'ip -all netns delete', shell=True)
                    for n in self.nslist:
                        self.app.ns[n].__del__()
                    self.nslist.clear()
                else:
                    for n in gl_args[1].split(';'):
                        subprocess.Popen(f'ip netns delete {n}', shell=True)
                        self.nslist.pop(n)
                        self.app.ns[n].__del__()
                            

    def do_lnk(self, arg):
        """
        -l, --list                                          lists all links
        -la, --list-available                               lists available links
        -a=N, --add=N                                       add link-peers with number of N
        -a, --add PEER_A:PEER_B[;PEER_C:PEER_D;...]         add one or more links 
                                                             with seperated by ';'
                                                             only for veth
        -d, --del [all] | PEER_A[;PEER_B...;]               delete one or more namespace with 
                                                             seperated by ';' or delete all
        -j, --join NAMESPACE-PEER_A[;PEER_B...;]            add link devices to namespace
        -ji, --join-ip-address NAMESPACE-PEER_A>IPADDRESS[;PEER_B>IPADDRESS...;]
                                                            add link devices to namespace
                                                             with ip address
        -r, --remove NAMESPACE-PEER_A[;PEER_B...;]          remove link devices from namespace
        """
        gl_args = arg.split(" ")

        if gl_args[0] in ("-l", "--list"):
            for k in self.lnklist:
                print(k)
            
        elif gl_args[0] in ("-la", "--list-available"):
            for k in self.avalnklist:
                print(k)

        elif gl_args[0] in ("-a", "--add"):
            if not len(gl_args) > 1:
                print("At least one argument is needed.")
            else:
                for lnk in gl_args[1].split(';'):
                    pr = lnk.split(':')
                    if not lnk in ("all","1"):
                        if len(pr) != 2:
                            print(f'{lnk} is invalid peer name. Passed.')
                        else:
                            subprocess.Popen(f'ip link add {pr[0]} type veth peer name {pr[1]}', shell=True)
                            self.lnklist[pr[0]] = Link(pr[0],"veth",pr[1])
                            self.lnklist[pr[1]] = Link(pr[1],"veth",pr[0])
                            self.avalnklist[pr[0]] = self.lnklist[pr[0]]
                            self.avalnklist[pr[1]] = self.lnklist[pr[1]]
                            self.app.peers[pr[0]] = GUI_Dev(self.app, (0,0), self.app.host, self.lnklist[pr[0]])
                            self.app.peers[pr[1]] = GUI_Dev(self.app, (0,0), self.app.host, self.lnklist[pr[1]])
                    else:
                        print(f'{lnk} is invalid link name. Passed.')
                        
        elif gl_args[0].split('=')[0] in ("-a", "--add"):
            num = int(gl_args[0].split('=')[1])
            for _ in range(num):
                peerA, peerB = f'veth{self.peerIndex}', f'veth{self.peerIndex+1}'
                subprocess.Popen(f'ip link add {peerA} type veth peer name {peerB}', shell=True)
                self.lnklist[peerA] = Link(peerA,"veth",peerB)
                self.lnklist[peerB] = Link(peerB,"veth",peerA)
                self.avalnklist[peerA] = self.lnklist[peerA]
                self.avalnklist[peerB] = self.lnklist[peerB]
                self.app.peers[peerA] = GUI_Dev(self.app, (0,0), self.app.host, self.lnklist[peerA])
                self.app.peers[peerB] = GUI_Dev(self.app, (0,0), self.app.host, self.lnklist[peerB])
                self.peerIndex+=2

        elif gl_args[0] in ("-d", "--del"):
            if not len(gl_args) > 1:
                print("At least one argument is needed.")
            else:
                if gl_args[1] == "all":
                    peerl = []
                    for lnk in self.avalnklist: # self.lnklist
                        if not lnk in peerl:
                            subprocess.Popen(f'ip link delete {lnk}', shell=True)
                            peerl.append(self.lnklist[lnk].peer)
                    self.lnklist.clear()
                    self.avalnklist.clear()
                    self.peerIndex = 0
                else:
                    for lnk in gl_args[1].split(';'):
                        peer = self.avalnklist[lnk].peer
                        subprocess.Popen(f'ip link delete {lnk}', shell=True)
                        self.lnklist.pop(peer)
                        self.avalnklist.pop(peer)
                        self.lnklist.pop(lnk)
                        self.avalnklist.pop(lnk)
    
        elif gl_args[0] in ("-j", "--join"):
            ns = gl_args[1].split('-')[0]
            for lnk in gl_args[1].split('-')[1].split(';'):
                if not system(f'ip link set {lnk} netns {ns}'):
                    self.nslist[ns].device[lnk] = self.avalnklist.pop(lnk)

        elif gl_args[0] in ("-ji", "--join-ip-address"):
            ns = gl_args[1].split('-')[0]
            for pkg in gl_args[1].split('-')[1].split(';'):
                lnk, addr = pkg.split('>')
                if not system(f'ip link set {lnk} netns {ns}'):
                    if not system(f'ip netns exec {ns} ifconfig {lnk} {addr} up'):
                        self.avalnklist[lnk].address = addr
                        self.avalnklist[lnk].state = 1
                        self.lnklist[lnk].address = addr
                        self.nslist[ns].device[lnk] = self.avalnklist.pop(lnk)
                        self.app.peers[lnk].coord = (0, 0)
                        self.app.peers[lnk].master = self.app.ns[ns]
                        self.app.ns[ns].dev[lnk] = self.app.peers[lnk]
                        self.app.peers[lnk].address = addr
                        self.app.peers[lnk].update()


        elif gl_args[0] in ("-r", "--remove"):
            ns = gl_args[1].split('-')[0]
            for lnk in gl_args[1].split('-')[1].split(';'):
                if not system(f'ip netns exec {ns} ip link set {lnk} netns 1'):
                    self.avalnklist[lnk] = self.nslist[ns].device.pop(lnk)

    def do_debug(self, arg):
        """Debug tool. Prints args of self."""
        print("Namespaces", self.nslist)
        print("Links", self.lnklist)
        print("Availables", self.avalnklist)



class Namespace(Cmd):

    def __init__(self, name) -> None:
        super().__init__(completekey='tab', stdin=None, stdout=None)
        super.__setattr__(self, "prompt", f'{name}> ')
        self.name = name
        self.device = {}

    def __repr__(self) -> str:
        return f'{[self.device[k] for k in self.device]}'

    def do_clear(self, arg):
        """Clears screen."""
        system("clear")

    def do_exit(self, arg):
        """Exits namespace and returns global scope."""
        return True

    def do_debug(self, arg):
        """Debug tool. Prints args of self."""
        print(self)

    def do_X(self, arg):
        """Do executaion in namespace"""
        system(f'ip netns exec {self.name} {arg}')

    def do_fw(self, arg):
        """For ipv4 forwarding"""
        self.do_X("sysctl -w net.ipv4.ip_forward=1")

    def do_gateway(self, arg: str):
        """-D=DEVICE -G=GATEWAY [-N=NETWORK/MASK]       set given gateway for given device
                                                         and given network if it is given.
                                                         If not given the network is default.
        """
        args = arg.split(" ")
        if len(args) == 2:
            device = args[0].split("-D=")[1]
            gateway = args[1].split("-G=")[1]
            network = "default"
        if len(args) == 3:
            device = args[0].split("-D=")[1]
            gateway = args[1].split("-G=")[1]
            network = args[2].split("-N=")[1]

        self.do_X(f'ip route add {network} dev {device} via {gateway}')


