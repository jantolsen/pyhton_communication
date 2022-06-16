# UDP Server
# ------------------------------
# Description:
# Server side for sending UDP packages

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

serverMessage = "Hello UPD Client (Matlab)"
byte2send = str.encode(serverMessage)

# Constants
# ------------------------------
# Address family
IPv4 = socket.AF_INET
IPv6 = socket.AF_INET6
BLUETOOTH = socket.AddressFamily.AF_BLUETOOTH

# Communication protocols
UDP = socket.SOCK_DGRAM
TCP = socket.SOCK_STREAM

# Server Configuration
# ------------------------------
# Create a datagram socket
serverSocket = socket.socket(IPv4, UDP) 

# Bind address and IP
serverSocket.bind((UDP_IP, UDP_Port))

# Connection
# ------------------------------

# Report to terminal
print("UPD Server: Up and listening")

# Start communication loop
while(True):
    
    # Connection
    data, address = serverSocket.recvfrom(bufferSize)

    # Received data
    connectionIP = "Client IP Address: " + format(address)
    connectionMessage = "Message from Client: " + format(struct.unpack('<fff', data))
    
    # Print data
    print(connectionIP)
    print(connectionMessage)

    # Send data
    address_matlab = ('127.0.0.1', 20002)
    serverSocket.sendto(data, address_matlab)
    print("UPD Server: Message sent to: {}".format(address_matlab))

        

    





