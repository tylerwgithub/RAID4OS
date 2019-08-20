'''
THIS IS A MEMORY MODULE ON THE SREVER WHICH ACTS LIKE MEMORY OF FILE SYSTEM. ALL THE OPERATIONS REGARDING THE FILE SYSTEM OPERATES IN 
THIS MODULE. THE MODULE HAS POINTER TO DISK AND HAS EXACT SAME LAYOUT AS UNIX TYPE FILE SYSTEM.
'''  
import pickle as Serdes
import Memory
from xmlrpclib import Fault as ServerError
from pickle import PickleError
from socket import error as SocketError

#OPERATIONS ON FILE SYSTEM
class Operations():
    def __init__(self):
        #POINTER TO MEMORY OBJECT
        Memory.Initialize()
        self.memory_obj = Memory.Operations()

    #GIVES ADDRESS OF INODE TABLE
    def addr_inode_table(self):
        saddr_inode_blocks = ''
        try:
            addr_inode_blocks = self.memory_obj.addr_inode_table()
            saddr_inode_blocks = Serdes.dumps(addr_inode_blocks)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return saddr_inode_blocks

    #RETURNS THE DATA OF THE BLOCK
    def get_data_block(self, sblock_number):
        sdata_block = ''
        try:
            block_number = Serdes.loads(sblock_number)
            data_block = self.memory_obj.get_data_block(block_number)
            sdata_block = Serdes.dumps(data_block)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return sdata_block

    #RETURNS THE BLOCK NUMBER OF AVAIALBLE DATA BLOCK  
    def get_valid_data_block(self):
        sdata_block = ''
        try:
            data_block = self.memory_obj.get_valid_data_block()
            sdata_block = Serdes.dumps(data_block)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return sdata_block

    #REMOVES THE INVALID DATA BLOCK TO MAKE IT REUSABLE
    def free_data_block(self, sblock_number):
        try:
            block_number = Serdes.loads(sblock_number)
            self.memory_obj.free_data_block(block_number)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return

    #WRITES TO THE DATA BLOCK
    def update_data_block(self, sblock_number, sblock_data):
        try:
            block_number = Serdes.loads(sblock_number)
            block_data = Serdes.loads(sblock_data)
            self.memory_obj.update_data_block(block_number, block_data)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return

    #UPDATES INODE TABLE WITH UPDATED INODE
    def update_inode_table(self, sinode, sinode_number):
        try:
            inode = Serdes.loads(sinode)
            inode_number = Serdes.loads(sinode_number)
            self.memory_obj.update_inode_table(inode, inode_number)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return

    #RETURNS THE INODE FROM INODE NUMBER
    def inode_number_to_inode(self, sinode_number):
        saddr_inode_blocks = ''
        try:
            inode_number = Serdes.loads(sinode_number)
            addr_inode_blocks = self.memory_obj.inode_number_to_inode(inode_number)
            saddr_inode_blocks = Serdes.dumps(addr_inode_blocks)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return saddr_inode_blocks

    #SHOWS THE STATUS OF DISK LAYOUT IN MEMORY
    def status(self):
        sret_status = ''
        try:
            ret_status = self.memory_obj.status()
            sret_status = Serdes.dumps(ret_status)
        except (ServerError, SocketError, PickleError) as error:
            print ("MemoryInterface_RPC Error: "), error
        #Catch other exceptions
        except Exception as error:
            print ("MemoryInterface_RPC Error: "), error
        return sret_status
