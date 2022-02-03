
import json
import queue
import socket
from socket import AF_INET, AF_INET6
import struct
import threading
from dataclasses import dataclass
from threading import Thread
from typing import overload

import requests


def get_own_ipv4():
    try:
        ip = requests.get('https://api4.ipify.org').content.decode('utf8')
        return ip
    except requests.RequestException:
        return None
        

def get_own_ipv6():
    try:
        ip = requests.get('https://api6.ipify.org').content.decode('utf8')
        return ip
    except requests.RequestException:
        return None


def encode_json(obj):
    encoded = json.dumps(obj).encode("UTF-8")
    bytes = struct.pack("!L", len(encoded)) + encoded
    return bytes


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    # thanks goes to https://stackoverflow.com/a/17668009/17248078
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data



@dataclass
class Message:
    adr: tuple
    data: any

class Node:
    def __init__(self, host_port, af=AF_INET):
        self.host = ("0.0.0.0", host_port)
        self.inq = queue.Queue()
        self.outq = queue.Queue()

        self.shutdown = False
        self.server = socket.socket(af, socket.SOCK_STREAM)
        self.server.bind(self.host)
        self.server.settimeout(1)

        def server_proc():
            self.server.listen()
            print("Server started")

            while not self.shutdown:
                try:
                    conn, addr = self.server.accept()
                except socket.timeout:
                    continue
                except socket.error as e:
                    print("Some other server error:", e)
                    continue
                finally:
                    if self.shutdown:
                        break

                count, = struct.unpack("!L", recvall(conn, 4))
                obj = json.loads(recvall(conn, count))
                self.inq.put(Message(addr, obj))

            self.server.close()
            print("Server finished")


        self.server_thread = threading.Thread(target=server_proc)
        self.server_thread.start()

        def client_proc():
            print("Client started")
            while not self.shutdown:
                try:
                    message = self.outq.get(timeout=1)
                except queue.Empty:
                    continue
                except socket.error as e:
                    print("Some other client error:", e)
                    continue
                finally:
                    if self.shutdown:
                        break
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect(message.adr)
                    client.sendall(encode_json(message.data))
            print("Client finished")


        self.client_thread = threading.Thread(target=client_proc)
        self.client_thread.start()

    def receive(self):
        return self.inq.get()

    def send(self, message):
        self.outq.put(message)

    def ipv4(self):
        return get_own_ipv4()
    
    def host_ipv4(self):
        ipv4 = get_own_ipv4()
        return ipv4, self.host[1] if ipv4 else None

    def ipv6(self):
        return get_own_ipv6()
    
    def host_ipv6(self):
        ipv6 = get_own_ipv6()
        return ipv6, self.host[1] if ipv6 else None

    def close(self):
        self.shutdown = True
        self.server_thread.join()
        self.client_thread.join()
