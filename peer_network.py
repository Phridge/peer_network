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
print(node.ipv6_all())

node.close()

