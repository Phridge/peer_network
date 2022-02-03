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

print(node.public_ipv4())
print(node.local_ipv4())
print(node.public_ipv6())
print(node.local_ipv6())


node.close()