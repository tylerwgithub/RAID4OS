'''
THIS IS A MEMORY MODULE ON THE SREVER WHICH ACTS LIKE MEMORY OF FILE SYSTEM. ALL THE OPERATIONS REGARDING THE FILE SYSTEM OPERATES IN 
THIS MODULE. THE MODULE HAS POINTER TO DISK AND HAS EXACT SAME LAYOUT AS UNIX TYPE FILE SYSTEM.
'''  
import xmlrpclib as ClientRPC
from xmlrpclib import Fault as ClientError
import pickle as Serdes
from pickle import PickleError
from socket import error as SocketError
import config
import socket
# Timeout for broken connections
socket.setdefaulttimeout(config.SOCKET_TIMEOUT)

numservers = config.NUM_OF_SERVERS

class Initialize():
    def __init__(self):
        print "Initializing memory on RPC"
        return

#OPERATIONS ON FILE SYSTEM
class Operations():
    def Initialize_My_FileSystem(self):
        #POINTER TO SERVER OBJECT
        self.startpoint = config.SERVER_PORT_BEGIN
        self.memory_server = []
        try:
            for i in range(self.startpoint, (self.startpoint + numservers)):
                print "Connecting to Server ", i
                self.memory_server.append(ClientRPC.ServerProxy("http://localhost:" + str(i) + "/", allow_none=True))
        except (ClientError, SocketError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error

        return

    #GIVES ADDRESS OF INODE TABLE
    def addr_inode_table(self):
        addr_inode_blocks = -1
        try:
            saddr_inode_blocks = self.memory_server.addr_inode_table()
            addr_inode_blocks = Serdes.loads(saddr_inode_blocks)
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), error
        return addr_inode_blocks

    #RETURNS THE DATA OF THE BLOCK
    def get_data_block(self, server_number, block_number):
        data_block = ''
        try:
            sblock_number = Serdes.dumps(block_number)
            sdata_block = self.memory_server[server_number].get_data_block(sblock_number)
            data_block = Serdes.loads(sdata_block)
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
        
        #print "data block ", data_block
        return ''.join(data_block)

    #RETURNS THE BLOCK NUMBER OF AVAIALBLE DATA BLOCK  
    def get_valid_data_block(self, server_number):
        data_block = -1
        try:
            sdata_block = self.memory_server[server_number].get_valid_data_block()
            data_block = Serdes.loads(sdata_block)
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
        
        return data_block

    #REMOVES THE INVALID DATA BLOCK TO MAKE IT REUSABLE
    def free_data_block(self, server_number, block_number):
        ret_val = 0
        try:
            sblock_number = Serdes.dumps(block_number)
            self.memory_server[server_number].free_data_block(sblock_number)
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            ret_val = -1
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            ret_val = -1
        return ret_val

    #WRITES TO THE DATA BLOCK
    def update_data_block(self, server_number, block_number, block_data):
        ret_val = 0
        try:
            sblock_number = Serdes.dumps(block_number)
            sblock_data = Serdes.dumps(block_data)
            self.memory_server[server_number].update_data_block(sblock_number, sblock_data)
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            ret_val = -1
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
            ret_val = -1
        return ret_val

    #UPDATES INODE TABLE WITH UPDATED INODE
    def update_inode_table(self, server_number, inode, inode_number):
        try:
            sinode = Serdes.dumps(inode)
            sinode_number = Serdes.dumps(inode_number)
            self.memory_server[server_number].update_inode_table(sinode, sinode_number)
        except (ClientError, SocketError, PickleError) as error:
            #print ("MemoryInterface_RPC Error: "), error
            pass
        #Catch other exceptions
        except Exception as error:
            #print ("MemoryInterface_RPC Error: "), error
            pass
        return

    #RETURNS THE INODE FROM INODE NUMBER
    def inode_number_to_inode(self, server_number, inode_number):
        addr_inode_blocks = False
        try:
#             print server_number, inode_number
            sinode_number = Serdes.dumps(inode_number)
            saddr_inode_blocks = self.memory_server[server_number].inode_number_to_inode(sinode_number)
#             print saddr_inode_blocks
            addr_inode_blocks = Serdes.loads(saddr_inode_blocks)
#             print addr_inode_blocks
            
        except (ClientError, SocketError, PickleError) as error:
            #print ("MemoryInterface_RPC Error: "), error
            pass
        #Catch other exceptions
        except Exception as error:
            #print ("MemoryInterface_RPC Error: "), error
            pass
        return addr_inode_blocks


    #SHOWS THE STATUS OF DISK LAYOUT IN MEMORY
    def status(self, server_number):
        try:
            sret_status = self.memory_server[server_number].status()
            ret_status = Serdes.loads(sret_status)
            return ret_status
        except (ClientError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error Server: "), server_number, error
        return ""

#------------------------------------------------------------ obj = Operations()
#----------------------------------------------- b = obj.get_valid_data_block(2)
#----------------------------------- obj.update_data_block(2, b, "hello world!")
#----------------------------------------------------------- print obj.status(2)
