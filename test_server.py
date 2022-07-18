# UDP Communication Server
# ------------------------------
# Description:
# UDP Communication Server for 
# sending and recieving UDP packages

# Version
# ------------------------------
# 0.0   -   Initial version
#           [17.07.2022] - Jan T. Olsen

# Import packages
import logging
import sys
import socket
import select
import time

# Import Toolbox
import comm_toolbox as CommToolbox

# Import Class Files
from lib.generic_commdata import GenericCommClass

# Logging Configuration
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',datefmt='%H:%M:%S', level=logging.DEBUG)

# UDP Server Class
# ------------------------------
class UDPServer():

    # Class constructor
    # ------------------------------
    # Assign default class arguments
    def __init__(self, ip = '127.0.0.1', port = 10000) -> None:

        # Class attributes
        # ------------------------------
        # If no class arguments where given default values are used
        self.ip = ip 
        self.port = port
        self.address = (ip, port)

        # Server Configuration
        self.config()

    # Configure Server
    # ------------------------------
    def config(self):

        # Create a UDP socket
        self.server_socket = socket.socket(CommToolbox.COMM_CONST.IPV4, CommToolbox.COMM_CONST.UDP) 
        # self.server_socket = socket.socket(CommToolbox.COMM_CONST.IPV4, CommToolbox.COMM_CONST.TCP) 

        # Enable re-use of Address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        # Bind address and IP
        self.server_socket.bind(self.address)

        # Listen to new TCP connections
        # self.server_socket.listen()

        # Disable blocking
        self.server_socket.setblocking(False)

        # Define socket-lists to be used with select() functionality
        self.input_sockets = [self.server_socket]
        self.output_sockets = [self.server_socket]
        self.error_sockets = [self.server_socket]

        # Report
        logging.info('UDP Server: Successfully configured with address: (%s:%s)', format(self.ip), format(self.port))


    # Establish Server Connection
    # ------------------------------
    def connect(self):
        
        # Report
        logging.info('UDP Server: Establish connection')

        # Connection Loop
        # ------------------------------
        while True:
            
            # Try to establish a connection with sockets 
            try:

                # Calls Unix select() system call or Windows select() WinSock call with three parameters:
                #   - rlist - sockets to be monitored for incoming data
                #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
                #   - xlist - sockets to be monitored for exceptions
                #   - timeout - timeout (seconds) before blocking-call is released, if no connection is established
                # Returns lists:
                #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
                #   - writing - sockets ready for data to be send thru them
                #   - errors  - sockets with some exceptions
                # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
                read_sockets, write_sockets, exception_sockets = select.select(self.input_sockets, 
                                                                            [], #self.output_sockets, 
                                                                            self.error_sockets,
                                                                            CommToolbox.COMM_CONST.TIMEOUT)

                # Iterate over Read-Sockets
                # ------------------------------
                for socket in read_sockets:
                    
                    print('reading')
                
                # Iterate over Write-Sockets
                # ------------------------------
                for socket in write_sockets:
                    
                    print('writing')

                # Handle Exception-Sockets
                # ------------------------------
                for socket in exception_sockets:

                    # If exception-socket exist in input-sockets
                    if socket in self.input_sockets:
                        # Remove entry from inputs-sockets
                        self.input_sockets.remove(socket)

                    # If exception-socket exist in output-sockets
                    if socket in self.output_sockets:
                        # Remove entry from outputs-sockets
                        self.output_sockets.remove(socket)

                    # Report
                    logging.warning('UDP Server: Exception socket')

                    # Close exception-socket
                    socket.close()

                # Timeout: No sockets are found
                # ------------------------------
                # (read-, write-, and expection-sockets are empty)
                if not (read_sockets and write_sockets and exception_sockets):

                    # Report
                    logging.warning('UDP Server: Connection timeout, retrying ...')

            # Exception(s)
            except KeyboardInterrupt:
                logging.exception('UDP Server: keyboard interrupt, exiting')
                sys.exit()
    

def main():
    logging.info('Hello World')

# Main
# ------------------------------
if __name__ == "__main__":

    # main()

    udp_server = UDPServer()

    udp_server.connect()


