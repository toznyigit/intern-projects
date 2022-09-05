from secrets import choice
import tkinter as tk
from link import Link
from functools import partial
import subprocess
import random

WIDTH = 100
HEIGHT = 100
# ns_color = ["#e6b0aa", "#f5b7b1", "#d7bde2", "#d2b4de", "#a9cce3", "#aed6f1", "#a3e4d7", "#a2d9ce", "#edbb99", "#f5cba7", "#fad7a0", "#f9e79f", "#abebc6", "#a9dfbf"]
# dev_color = ["#85c1e9", "#7fb3d5", "#bb8fce", "#c39bd3", "#f1948a", "#d98880", "#f8c471", "#f7dc6f", "#82e0aa", "#7dcea0", "#73c6b6", "#76d7c4", "#f0b27a", "#e59866"]
ns_color = ["#e6b0aa", "#d7bde2", "#a9cce3", "#a3e4d7", "#edbb99", "#fad7a0", "#abebc6"]
# dev_color = ["#85c1e9", "#bb8fce", "#f1948a", "#f8c471", "#82e0aa", "#73c6b6", "#f0b27a"]
dev_color = ["#566573"]
class GUI(tk.Tk):
    def __init__(self, args):
        super().__init__()

        # configure the root window
        self.title('Network Graph')
        self.geometry('800x800')
        self.configure(bg='#d6dbdf')
        self.board = tk.Canvas(self, bg="white", width=700, height=500)
        self.host = GUI_Ns_dummy()

        # root elements
        self.x = 0
        self.y = 0
        self.active_object = None
        self.ns = {}
        self.peers = {}

        # button
        self.button = tk.Button(self, text='Quit')
        self.button['command'] = self.quit
        self.button.pack()
        self.board.pack()

        # label
        self.name = tk.Label(self, text='', bg='#d6dbdf')
        self.name.pack()
        self.ip = tk.Label(self, text='', bg='#d6dbdf')
        self.ip.pack()

        # control

        self.control_frame_left = tk.Frame(self, bg='#d6dbdf')
        self.control_frame_left.pack(side=tk.LEFT)
        self.control_frame_right = tk.Frame(self, bg='#d6dbdf')
        self.control_frame_right.pack(side=tk.RIGHT)

        self.scrollbar = tk.Scrollbar(self.control_frame_right, orient='vertical')
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.text = tk.Text(self.control_frame_right, font=("Georgia, 7"), yscrollcommand=self.scrollbar.set, state="disable", width=80, bg='#d6dbdf')
        self.scrollbar.config(command=self.text.yview)
        self.text.pack()

        # self.placeholder = tk.Label(self.control_frame_left, text="NAMESPACE", bg='#d6dbdf', font="bold")
        self.namespace_label = tk.Label(self.control_frame_left, text="", bg='#d6dbdf', font='bold')
        self.input_label = tk.Label(self.control_frame_left, text="Target Address", bg='#d6dbdf')
        self.input_text = tk.Entry(self.control_frame_left)

        self.btn_ping = tk.Button(self.control_frame_left, text="Ping", command=self.ping)
        self.btn_wget = tk.Button(self.control_frame_left, text="Wget", command=self.wget)
        self.btn_iptable = tk.Button(self.control_frame_left, text="Show Iptable", command=self.show_iptables)
        self.btn_route = tk.Button(self.control_frame_left, text="Show Route", command=self.show_route)

        # self.placeholder.grid(row=0,column=2)
        self.namespace_label.grid(row=1,column=1,columnspan=3)
        self.input_text.grid(row=2,column=1,columnspan=3)
        self.btn_ping.grid(row=2,column=0)
        self.btn_wget.grid(row=2,column=4)
        self.btn_iptable.grid(row=3,column=1)
        self.btn_route.grid(row=3,column=3)


        # color iter
        self.ns_color = 0
        self.dev_color = 0

        self.board.bind('<Button-3>', self.on_click)
        self.board.bind('<Enter>', lambda event: self.name.configure(text="host"))
        self.board.bind('<Leave>', lambda event: self.name.configure(text=""))

    def set_ns(self, args):
        for key in args:
            if not key in self.ns:
                self.ns[key] = args[key]
            else:
                self.ns[key] += args[key]

    def quit(self):
        self.destroy()

    def on_click(self, event):
        self.namespace_label.configure(text="")
        self.active_object = None

    def show_route(self):
        out = None
        if self.active_object:
            out = subprocess.Popen(['ip', 'netns', 'exec', self.active_object, 'route', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            out = subprocess.Popen(['route', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout, stderr = out.communicate()
        out.kill()
        self.update_out(stdout)
    
    def show_iptables(self):
        if self.active_object:
            out = subprocess.Popen(['ip', 'netns', 'exec', self.active_object, 'iptables', '-L', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            out = subprocess.Popen(['iptables', '-L', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout, stderr = out.communicate()
        out.kill()
        self.update_out(stdout)

    def ping(self):
        if self.active_object:
            out = subprocess.Popen(['ip', 'netns', 'exec', self.active_object, 'ping', '-w 1', self.input_text.get()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            out = subprocess.Popen(['ping', '-w 1', self.input_text.get()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        stdout, stderr = out.communicate()
        out.kill()
        self.update_out(stdout)

    def wget(self):
        if self.active_object:
            out = subprocess.Popen(['ip', 'netns', 'exec', self.active_object, 
                'wget', '--timeout=1', '--tries=1', '--no-check-certificate', '--no-cache', '--spider', self.input_text.get()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            out = subprocess.Popen(['wget', '--timeout=1', '--tries=1', '--no-check-certificate', '--no-cache', '--spider', self.input_text.get()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        stdout, stderr = out.communicate()
        out.kill()
        self.update_out(stdout)        

    def update_out(self, stdout):
        self.text.configure(state='normal')
        self.text.delete("1.0",tk.END)
        self.text.insert(tk.END, stdout.decode("utf-8"))
        self.text.configure(state='disable')

    def find_avail_coord(self, xrange, yrange):
        return random.randrange(0,xrange), random.randrange(0,yrange)

class GUI_Ns():
    def __init__(self, app, coord, ns):
        self.app = app
        self.coord = app.find_avail_coord(700-WIDTH, 500-HEIGHT)
        self.size = (WIDTH, HEIGHT)
        self.ns = ns
        self.name = ns.name
        self.id = self.app.board.create_rectangle(self.coord[0], self.coord[1], self.coord[0]+WIDTH, self.coord[1]+HEIGHT, outline='black', fill=ns_color[self.app.ns_color%len(ns_color)])
        self.dev = {}
        self.app.board.tag_bind(self.id, '<B1-Motion>', partial(self.on_motion))
        self.app.board.tag_bind(self.id, '<Button-1>', partial(self.on_click))
        self.app.board.tag_bind(self.id, '<Enter>', lambda event: self.app.name.configure(text=self.name))
        self.app.board.tag_bind(self.id, '<Leave>', lambda event: self.app.name.configure(text="host"))

        self.app.ns_color+=1

    def on_motion(self, event):
        self.coord = (max(0, min(event.x-WIDTH/2, 700-self.size[0])),
                      max(0, min(event.y-HEIGHT/2, 500-self.size[0])))
        self.app.board.moveto(self.id, self.coord[0], self.coord[1])
        for d in self.dev:
            self.app.board.moveto(self.dev[d].id, self.dev[d].coord[0]+self.coord[0], self.dev[d].coord[1]+self.coord[1])
            if self.dev[d].connection:
                self.dev[d].connection.on_motion(event, self.dev[d])

    def on_click(self, event):
        self.app.namespace_label.configure(text=self.name)
        self.app.active_object=self.name

    def __del__(self):
        self.app.ns.pop(self.name)
        for d in self.dev:
            self.dev[d].__del__()
        self.app.board.delete(self.id)

class GUI_Dev():
    def __init__(self, app, coord, master, lnk):
        self.app = app
        self.master = master
        self.coord = app.find_avail_coord(700, 500)
        self.size = (20, 20)
        self.lnk = lnk
        self.name = lnk.name
        self.address = lnk.address
        self.connection = None
        self.init_pair(self.lnk.peer)
        self.id = self.app.board.create_rectangle(self.coord[0], self.coord[1], self.coord[0]+self.size[0], self.coord[1]+self.size[1], outline='black', fill=dev_color[self.app.dev_color%len(dev_color)])
        # self.app.board.moveto(self.id, self.master.coord[0], self.master.coord[1])
        self.app.board.tag_bind(self.id, '<B1-Motion>', partial(self.on_motion))
        self.app.board.tag_bind(self.id, '<Enter>', partial(self.on_enter))
        self.app.board.tag_bind(self.id, '<Leave>', partial(self.on_leave))

        self.app.dev_color+=1

    def on_motion(self, event):
        self.coord = (max(0, min(event.x-self.master.coord[0], self.master.size[0]-self.size[0])),
                      max(0, min(event.y-self.master.coord[1], self.master.size[1]-self.size[0])))
        self.app.board.moveto(self.id, self.coord[0]+self.master.coord[0], self.coord[1]+self.master.coord[1])
        if self.connection:
            self.connection.on_motion(event, self)

    def on_enter(self, event):
        self.app.name.configure(text=f'{self.master.name}@{self.name}')
        self.app.ip.configure(text=f'{self.address}')

    def on_leave(self, event):
        self.app.name.configure(text="")
        self.app.ip.configure(text="")

    def init_pair(self, name):
        for n in self.app.ns:
            for d in self.app.peers:
                if name==self.app.peers[d].name:
                    if self.connection: self.app.board.delete(self.connection.id)
                    self.connection = GUI_Line(self.app, self, self.app.peers[d])
                    self.app.peers[d].connection = self.connection

    def update(self):
        self.coord = self.app.find_avail_coord(WIDTH-self.size[0], HEIGHT-self.size[1])
        self.app.board.moveto(self.id, self.coord[0]+self.master.coord[0], self.coord[1]+self.master.coord[1])
        self.init_pair(self.lnk.peer)

    def __del__(self):
        self.connection.__del__()
        self.app.peers.pop(self.name)
        if self.app.peers.get(self.lnk.peer):
            self.app.peers[self.lnk.peer].master.dev.pop(self.lnk.peer)
            self.app.peers[self.lnk.peer].__del__()
        self.app.board.delete(self.id)


class GUI_Line():
    def __init__(self, app, dev_0, dev_1):
        self.dev_0 = dev_0
        self.dev_1 = dev_1
        self.app = app
        self.c_0 = tuple(sum(x) for x in zip(dev_0.coord, dev_0.master.coord, (10, 10)))
        self.c_1 = tuple(sum(x) for x in zip(dev_1.coord, dev_1.master.coord, (10, 10)))
        self.id = self.app.board.create_line(self.c_0+self.c_1, fill="black", width=2)

    def on_motion(self, event, dev):
        self.app.board.delete(self.id)
        if dev.name == self.dev_0.name:
            self.c_0 = tuple(sum(x) for x in zip(self.dev_0.coord, self.dev_0.master.coord, (10, 10)))
            self.id = self.app.board.create_line(self.c_0+self.c_1, fill="black", width=2)
        else:
            self.c_1 = tuple(sum(x) for x in zip(self.dev_1.coord, self.dev_1.master.coord, (10, 10)))
            self.id = self.app.board.create_line(self.c_0+self.c_1, fill="black", width=2)

    def __del__(self):
        self.app.board.delete(self.id)

class GUI_Ns_dummy():
    def __init__(self):
        self.name = "host"
        self.coord = (0,0)
        self.size = (700,500)