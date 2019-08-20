from SimpleXMLRPCServer import SimpleXMLRPCServer
import threading
from multiprocessing import Process
import Memory_RPC as Memory
import config
import sys

class RaidServer():
    def __init__(self, server_port):
        self.memory = Memory.Operations()
        self.server = SimpleXMLRPCServer(("localhost", server_port), allow_none=True, logRequests=False)
        print "Listening on localhost : port ", server_port
        #Register all functions required for RPC
        self.server.register_instance(self.memory)
        self.server.register_introspection_functions()
        return
        
    def start_server(self):
        #Start the server
        self.server.serve_forever()
        
    def shutdown_server(self):
        #Shutdown the server
        self.server.shutdown()


if __name__ == "__main__":
    #server_port = config.SERVER_PORT_BEGIN
    server_port = 8003
    try:
        if len(sys.argv) > 1:
            server_port = int(sys.argv[1])
    except Exception as err:
        print err
        print "Port defaulted to ", server_port
    
    server = RaidServer(server_port)
    server_handle = threading.Thread(target=server.start_server, args = ( ))
    server_handle.start()
    
    inp = raw_input("Enter k to kill : ")
    while 'k' != inp:
        inp = raw_input()
    
    #kill the server
    server.shutdown_server()
    server_handle.running = False
    print "Server ", server_port, " Shutdown"