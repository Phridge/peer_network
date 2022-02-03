import logging
import socketserver
import threading
import socket
import time
import struct
import json
import functools
import jsonnode

node = jsonnode.Node(6969)
print(node.ipv4())

remote_ip = input("Remote IPv4:")

node.send(jsonnode.Message((remote_ip, 6969), {"Hello": "There!"}))
print(node.receive())

node.close()

