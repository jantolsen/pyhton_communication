# UDP Client
# ------------------------------
# Description:
# Client for sending and recieving UDP packages

# Version
# ------------------------------
# 0.0   -   Initial version
#           [16.06.2022] - Jan T. Olsen

# Import packages
import socket
import struct
import time

# UDP-Client Class
# ------------------------------
class UDPClient():

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
    def __init__(self, RemoteAddress=None, RemotePort=None, BufferSize=None):
        
        # Class arguments and default values
        # ------------------------------
        # Set IP-Address as default value
        # If no argument value was given
        if RemoteAddress is None:
            self.remoteAddress = '127.0.0.1'
        # Set IP-Address equal to class input
        else:
            self.remoteAddress = RemoteAddress 

        # Set Port as default value
        # If no argument value was given
        if RemotePort is None:
            self.remotePort = 22010
        # Set IP-Address equal to class input
        else:
            self.remotePort = RemotePort 

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

    # UDP Client Configuration
    # ------------------------------
    def config(self):
        # Create a datagram socket
        self.clientSocket = socket.socket(self.IPV4, self.UDP) 

        # Report to terminal
        print("------------------------------")
        print("UPD Client: Successfully configured")
        print("IP Address: " + format(self.remoteAddress))
        print("Port: " + format(self.remotePort))
        print("------------------------------")

    # UDP Client Send Data
    # ------------------------------
    def sendData(self):

        # Data
        # ------------------------------

        # clientMessage = "Hello UPD Server (not yet matlab)"
        # byte2send = str.encode(clientMessage)

        axis1 = 45.0
        axis2 = 107.5
        axis3 = 0.33
        
        # Packing data
        axis_pos = struct.pack('!fff', axis1, axis2, axis3)

        bytes2send = axis_pos

        # Send data
        self.clientSocket.sendto(bytes2send, (self.remoteAddress, self.remotePort))

        # Report sent data
        print("\n")
        print("Data sent from Client:")
        print("------------------------------")
        print("     " + format(struct.unpack('!fff', bytes2send)))
        print("------------------------------")

        # Recieved Data
        data, remoteAddress = self.clientSocket.recvfrom(self.bufferSize)

        print("\n")
        print("Received Data:")
        print("------------------------------")
        print(" IP Address: " + format(remoteAddress[0]))
        print(" Port: " + format(remoteAddress[1]))
        print("------------------------------")
        print("     " + format(struct.unpack('!fff', data)))
        print("------------------------------")

if __name__ == "__main__":
    udpClient = UDPClient()

    udpClient.sendData()
