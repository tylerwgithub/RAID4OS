# Mapping functionalities
import config
import time
import MemoryInterface_RPC as Memory

filesystem = Memory.Operations()
#HANDLE FOR MEMORY OPERATIONS
class Operations():
    def __init__(self):
        self.vblock_mapper = {} # Dictionary to store Virtual -> Actual Block Number mapping
        self.parity_mapper = {} # Dictionary to store Virtual -> Actual Block Number mapping for parity disk
        self.numservers = config.NUM_OF_SERVERS
        self.num_data_servers = config.NUM_OF_DATA_SERVERS
        self.client_blknum_counter = config.VIRTUAL_BLOCK_START
    
    #REQUEST TO BOOT THE FILE SYSTEM
    def Initialize_My_FileSystem(self):
        print("Filesystem Initializing......")
        for server_number in range(self.numservers):
            print("Initializing Disk " + str(server_number))
            Memory.Initialize()
        filesystem.Initialize_My_FileSystem()
        print("Filesystem Initialized!")
        return


    #REQUEST TO FETCH THE INODE FROM INODE NUMBER FROM SERVER
    def inode_number_to_inode(self, inode_number):
        for server_number in range(self.numservers):
            inode = filesystem.inode_number_to_inode(server_number, inode_number)
            if inode:
                return inode
        return False

    # Find XOR of 2 data blocks
    def xor_block_data(self, block1_data, block2_data):
        int_block1_data = []
        for i in range(len(block1_data)):
           int_block1_data.append(ord(block1_data[i]))
        for i in range(len(block1_data), config.BLOCK_SIZE):
            int_block1_data.append(0)
        
        int_block2_data = []
        for i in range(len(block2_data)):
           int_block2_data.append(ord(block2_data[i]))
        for i in range(len(block2_data), config.BLOCK_SIZE):
            int_block2_data.append(0)

        int_xored_block = [0] * config.BLOCK_SIZE
        for i in range(config.BLOCK_SIZE):
            int_xored_block[i] = int_block1_data[i] ^ int_block2_data[i]
        
        xored_block = ['\0'] * config.BLOCK_SIZE
        
        for i in range(config.BLOCK_SIZE):
            if int_xored_block[i] != 0:
                xored_block[i] = chr(int_xored_block[i])
        return ''.join(xored_block)

    # Collect data from active servers and provide data of the faulty server
    def correct_data_from_parity_server(self, faulty_server, block_number):
        parity_server_num = config.NUM_OF_SERVERS - 1
        if block_number in self.parity_mapper:
            print "Parity to the rescue"
            parity_blknum = self.parity_mapper[block_number]
        else:
            print "Doomed bro. Parity can't help"
            return
        
        parity_block_data = filesystem.get_data_block(parity_server_num, parity_blknum)
        recovered_block_data = parity_block_data
        for i in range(self.num_data_servers):
            if i == faulty_server : continue
            data_block = filesystem.get_data_block(i, block_number)
            recovered_block_data = self.xor_block_data(recovered_block_data, data_block)
        
        return ''.join(recovered_block_data)
        

    #REQUEST THE DATA FROM THE SERVER
    def get_data_block(self, block_number):
        server1, block_num1 = self.get_server1_and_block_num(block_number)
        stime = config.SLEEP_TIME
        ret_data = ''
        
        data1 = filesystem.get_data_block(server1, block_num1)
        
        # if nothing was returned from server 1 try server 2
        if data1 == '':
            print "Server ", server1, " not responding"
            print "Correcting data with parity server"
            data1 = self.correct_data_from_parity_server(server1, block_num1)
        
        ret_data = data1

        return ''.join(ret_data)

    #REQUESTS THE VALID BLOCK NUMBER FROM THE SERVER 
    def get_valid_data_block(self):
        self.client_blknum_counter += 1
        #3 copies, 2 to store data and one for parity
        server_list = [None] * (config.REDUNDANCY_COUNT)
        server_offset = self.client_blknum_counter % self.num_data_servers
        
        serverA_number = server_offset
        serverA_blknum = filesystem.get_valid_data_block(serverA_number)

        if -1 == serverA_blknum:
            serverA_number = (serverA_number + 1) % self.numservers
            serverA_blknum = filesystem.get_valid_data_block(serverA_number)

        # Push a list of server numbers and block number mappings for each vblock
        server_list[config.DATA_BLOCK_1] = (serverA_number, serverA_blknum)

        # Create a mapping of Virtual Block Number with list of Actual Block Numbers and their servers
        # Add the new Virtual block -> Actual block mapping to the dictionary
        self.vblock_mapper[self.client_blknum_counter] = server_list
        
        # Return the Virtual Block Number to the caller
        return self.client_blknum_counter
    
    
    def print_vnodes(self):
        print "Vnode size : ", len(self.vblock_mapper), " map:"
        for key, val in self.vblock_mapper.items():
            print key, " : ", val
        return
    
    
    def print_pnodes(self):
        print "Pnode size : ", len(self.parity_mapper), " map:"
        for key, val in self.parity_mapper.items():
            print key, " : ", val
        return


    def get_server1_and_block_num(self, block_number):
        #self.print_vnodes()
        #server, block_num = self.vblock_mapper[block_number][config.DATA_BLOCK_1]
        if block_number not in self.vblock_mapper:
            return (None, None)
        server_list = self.vblock_mapper[block_number]
        server, block_num = server_list[config.DATA_BLOCK_1]
        return (server, block_num)
    
    
    def get_server2_and_block_num(self, block_number):
        if block_number not in self.vblock_mapper:
            return (None, None)
        #server, block_num = self.vblock_mapper[block_number][config.DATA_BLOCK_2]
        server_list = self.vblock_mapper[block_number]
        server, block_num = server_list[config.DATA_BLOCK_2]
        return (server, block_num)
    
    
    def get_parity_server_and_block_num(self, block_number):
        if block_number not in self.vblock_mapper:
            return (None, None)
        #server, block_num = self.vblock_mapper[block_number][config.DATA_BLOCK_2]
        server_list = self.vblock_mapper[block_number]
        server, block_num = server_list[config.PARITY_BLOCK]
        return (server, block_num)


    #REQUEST TO MAKE BLOCKS RESUABLE AGAIN FROM SERVER
    def free_data_block(self, vblock_number):
        serverA_number, serverA_blknum = self.get_server1_and_block_num(vblock_number)
        
        status = 0
        if None != serverA_number:
            block_data = filesystem.get_data_block(serverA_number, serverA_blknum)
            # Update the parity of the block before deleting it
            self.update_parity_data(serverA_blknum, block_data)
            # Now that the parity is updated, go ahead delete the block from memory
            status = filesystem.free_data_block(serverA_number, serverA_blknum)
        if -1 == status:
            print ("Error VirtualBlockLayer: Server " + str(serverA_number) + " not responding")

        # Delete the old Virtual block entry in the dictionary 
        if vblock_number in self.vblock_mapper:
            del self.vblock_mapper[vblock_number]
        return

    
    #UPDATED PARITY DATA
    def update_parity_data(self, block_number, block_data):
        print "Updating parity for block ", block_number
        parity_server_num = config.NUM_OF_SERVERS - 1
        # Updating parity
        if block_number in self.parity_mapper:
            parity_blknum = self.parity_mapper[block_number]
        # Adding parity for the first time for given blocks
        else:
            parity_blknum = filesystem.get_valid_data_block(parity_server_num)
            self.parity_mapper[block_number] = parity_blknum
        
        parity_block_data = filesystem.get_data_block(parity_server_num, block_number)

        new_updated_parity = self.xor_block_data(block_data, parity_block_data)
        filesystem.update_data_block(parity_server_num, parity_blknum, ''.join(new_updated_parity))

        return ''.join(new_updated_parity)
    
    
    #REQUEST TO WRITE DATA ON THE THE SERVER
    def update_data_block(self, vblock_number, block_data):
        server1, block_num1 = self.get_server1_and_block_num(vblock_number)
        
        status = filesystem.update_data_block(server1, block_num1, block_data)
        if -1 == status:
            print ("Error VirtualBlockLayer: Server " + str(server1) + " not responding")

        parity_data = self.update_parity_data(block_num1, block_data)
        
        return
    
    
    #REQUEST TO UPDATE THE UPDATED INODE IN THE INODE TABLE FROM SERVER
    def update_inode_table(self, inode, inode_number):
        #self.print_vnodes()
        for server_number in range(self.numservers):
            filesystem.update_inode_table(server_number, inode, inode_number)
        return


    #REQUEST FOR THE STATUS OF FILE SYSTEM FROM SERVER
    def status(self):
        status = ""
        for server_number in range(self.numservers):
            status += str(server_number) + " : "
            status += filesystem.status(server_number)
        return status
    
    #REQUEST FOR THE STATUS OF FILE SYSTEM FROM SERVER
    def server_status(self, server_number):
        status = ""
        status += str(server_number) + " : "
        status += filesystem.status(server_number)
        return status


#------------------------------------------------------------ obj = Operations()
#------------------------------------------------ obj.Initialize_My_FileSystem()
#------------------------------------------------ b = obj.get_valid_data_block()
#----------------------------------------------------------- #obj.print_pnodes()
#-------------------------------------- obj.update_data_block(b, "hello world!")
#---------------------------------------------------- print obj.server_status(3)
#---------------------------------------------------- print obj.server_status(4)
#------------------------------------------------ c = obj.get_valid_data_block()
#----------------------------------------------------------- #obj.print_pnodes()
#------------------------------------- obj.update_data_block(c, "hello world!2")
#---------------------------------------------------- print obj.server_status(0)
#---------------------------------------------------- print obj.server_status(4)

#--------------------------------- obj.update_data_block(b, "hello wsdaf orld!")
#------------------------------ obj.update_data_block(b, "hellsadfasd o world!")
#-------------------------- obj.update_data_block(b, "hello wosdfasd as dfrld!")
#print obj.status()