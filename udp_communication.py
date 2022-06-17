# UDP Communication
# ------------------------------
# Description:
# Main Communication for sending and recieving UDP packages

# Version
# ------------------------------
# 0.0   -   Initial version
#           [16.06.2022] - Jan T. Olsen

# Import packages
from pickle import TRUE
import socket
import struct
import time

# UDP-Communication Class
# ------------------------------
class UDPCommunication():

    # Constants
    # ------------------------------
    # Address family
    IPV4 = socket.AF_INET
    IPV6 = socket.AF_INET6
    # BLUETOOTH = socket.AddressFamily.AF_BLUETOOTH

    # Communication protocols
    UDP = socket.SOCK_DGRAM
    TCP = socket.SOCK_STREAM

    # Class constructor
    def __init__(self, Address=None, Port=None, BufferSize=None):
        
        # Class arguments and default values
        # ------------------------------
        # Set IP-Address as default value
        # If no argument value was given
        if Address is None:
            self.address = '127.0.0.1'
        # Set IP-Address equal to class input
        else:
            self.address = Address 

        # Set Port as default value
        # If no argument value was given
        if Port is None:
            self.port = 22010
        # Set IP-Address equal to class input
        else:
            self.port = Port 

        # Set BufferSize as default value
        # If no argument value was given
        if BufferSize is None:
            self.bufferSize = 512
        # Set BufferSize equal to class input
        else:
            self.bufferSize = BufferSize 

        # Communication Configuration
        # ------------------------------
        self.config()



    # UDP Server Configuration
    # ------------------------------
    def config(self):
        # Create a datagram socket
        self.serverSocket = socket.socket(self.IPV4, self.UDP) 

        # Bind address and IP
        self.serverSocket.bind((self.address, self.port))

        # Report to terminal
        print("------------------------------")
        print("UPD Server: Successfully configured")
        print("IP Address: " + format(self.address))
        print("Port: " + format(self.port))
        print("------------------------------")

    # UDP Server Connection
    # ------------------------------
    def connect(self):
        # Connection
        data, remote_address = self.serverSocket.recvfrom(self.bufferSize)

        # Data
        udp_data = format(struct.unpack('!fff', data))

        # Report received data
        print("\n")
        print("Data received from Client:")
        print("------------------------------")
        print(" IP Address: " + format(remote_address[0]))
        print(" Port: " + format(remote_address[1]))
        print("------------------------------")
        print("     " + udp_data)
        print("------------------------------")

        # Send Data
        # (just returning incoming data)
        self.serverSocket.sendto(data, remote_address)

        print("\n")
        print("Data sent to Client:")
        print("------------------------------")
        print(" IP Address: " + format(remote_address[0]))
        print(" Port: " + format(remote_address[1]))
        print("------------------------------")
        print("     " + udp_data)
        print("------------------------------")

if __name__ == "__main__":
    udpComm = UDPCommunication()

    while(TRUE):
        udpComm.connect()