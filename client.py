from os import sys
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import Tk, simpledialog
import time

# host = str(input("Server's IP address: "))
host = '192.168.68.109'
port = int(input("Port to connect to: "))


class Client:

    def __init__(self, host, port):

        self.nickname = ""
        self.password = ""
        self.windows()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.timeout = 0

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)

        recv_thread = threading.Thread(target=self.receive, daemon=True)

        gui_thread.start()
        recv_thread.start()

    def windows(self):
        msg = tkinter.Tk()
        msg.withdraw()

        while not self.nickname:
            self.nickname = simpledialog.askstring(
                "Nickname", "Choose a nickname")
            if self.nickname == "" or self.nickname is None:
                msg.wm_protocol("WM_DELETE_WINDOW", sys.exit())
        #        print(self.nickname.lower())
        if self.nickname.lower() == 'admin':
            self.password = simpledialog.askstring(
                "Password", "Choose a pass for admin")
            if self.password is None or self.password == "":
                msg.wm_protocol("WM_DELETE_WINDOW", sys.exit())
            elif self.password != 'secretpass':
                while self.nickname.lower() == 'admin':
                    self.nickname = simpledialog.askstring(
                        "Nickname", "ADMIN NOT ALLOWED ANYMORE")
                    if self.nickname == "" or self.nickname is None:
                        msg.wm_protocol("WM_DELETE_WINDOW", sys.exit())

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.config(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(
            self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(
            self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack()
        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def stopm(self, msg):
        self.running = False
        msg.destroy()
        self.sock.close()
        exit(0)

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def write(self):

        mess = self.input_area.get('1.0', 'end')
        if mess != '\n':
            message = f"{self.nickname}: {mess}"
            self.sock.send(message.encode('ascii'))
            self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('ascii'))
                    if self.sock.recv(1024).decode('ascii') == "PASS":
                        self.sock.send(self.password.encode('ascii'))
#                    if self.sock.recv(1024).decode('ascii') == '!OK':
#                        duplicate = self.nickname
#                        print(duplicate)
#                        while duplicate == self.nickname:
#                            self.nickname = simpledialog.askstring(
#                                "Nickname", "Choose a nickname other than" + self.nickname)
#                            if self.nickname == "" or self.nickname == None:
#                                msg.wm_protocol("WM_DELETE_WINDOW", sys.exit())
                if self.gui_done:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message)
                    self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


client = Client(host, port)
