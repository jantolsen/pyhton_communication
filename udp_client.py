# UDP Client
# ------------------------------
# Description:
# Client side for sending UDP packages

# Version
# ------------------------------
# 0.0   -   Initial version
#           [11.06.2022] - Jan T. Olsen

# Import packages
import socket
import struct
import time

# Configuration
# ------------------------------
UDP_IP = "127.0.0.1"
UDP_Port = 20001
bufferSize = 1024

axis1 = 45.0
axis2 = 107.5
axis3 = 0.33


axis_pos = struct.pack('!fff', axis1, axis2, axis3)

clientMessage = "Hello UPD Server (not yet matlab)"
byte2send = str.encode(clientMessage)

# clientMessage = 123
byte2send = axis_pos


# Constants
# ------------------------------
# Address family
IPv4 = socket.AF_INET
IPv6 = socket.AF_INET6
BLUETOOTH = socket.AddressFamily.AF_BLUETOOTH

# Communication protocols
UDP = socket.SOCK_DGRAM
TCP = socket.SOCK_STREAM

# Client Configuration
# ------------------------------
# Create a datagram socket
clientSocket = socket.socket(IPv4, UDP) 

# Connection
# ------------------------------

# Send data
clientSocket.sendto(byte2send, (UDP_IP, UDP_Port))
print("UPD Client: Message sent to: {}".format(UDP_IP))

# Connection
data, address = clientSocket.recvfrom(bufferSize)

# Received data
connectionIP = "Server IP Address: {}".format(address)
connectionMessage = "Message from Server: {}".format(data)

        

        

    





