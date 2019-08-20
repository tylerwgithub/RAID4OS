'''
THIS MODULE IS INODE LAYER OF THE FILE SYSTEM. IT INCLUDES THE INODE DEFINITION DECLARATION AND GLOBAL HANDLE OF BLOCK LAYER OF API.
THIS MODULE IS RESPONSIBLE FOR PROVIDING ACTUAL BLOCK NUMBERS SAVED IN INODE ARRAY OF BLOCK NUMBERS TO FETCH DATA FROM BLOCK LAYER.
'''
import datetime, config, BlockLayer, InodeOps

#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()

class InodeLayer():
    #RETURNS BLOCK NUMBER FROM RESPECTIVE INODE DIRECTORY
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #RETURNS BLOCK DATA FROM INODE
    def INODE_TO_BLOCK(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number)


    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    def OFFSET_TO_BLOCK_INDEX(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        if index >= len(inode.blk_numbers):
            return -1
        return index

    def is_invalid_block_index(self, block_index):
        if -1 == block_index:
            return True
        return False

    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index):
        for i in range(index, len(inode.blk_numbers)):
            if inode.blk_numbers[i] != -1:
                interface.free_data_block(inode.blk_numbers[i])
            inode.blk_numbers[i] = -1

    #UPDATE FILE ACCESS TIME
    def update_read_time(self, inode):
        inode.update_accessed_time()
        return
    
    
    #UPDATE FILE ACCESS AND MODIFIED TIMES
    def update_write_time(self, inode):
        inode.update_accessed_time()
        inode.update_modified_time()
        return
    
    def is_invalid_read_offset(self, inode, offset):
        if offset > (len(inode.blk_numbers) * config.BLOCK_SIZE):
            return True
        return False
    
    
    def get_max_file_size(self, inode):
        return (len(inode.blk_numbers)*config.BLOCK_SIZE)
    
    
    def is_block_empty(self, inode, block_index):
        if -1 == inode.blk_numbers[block_index]:
            return True
        return False
    
    
    def get_offset_in_block(self, offset):
        return (offset % config.BLOCK_SIZE)
    
    
    def write_blocks_to_mem(self, block_index, dataBlocks):
        for block in dataBlocks:
            interface.update_data_block(block_index)
            block_index += 1
        return
    
    
    #DELETE BLOCKS STARTING FROM THE INDEX PROVIDED
    def empty_further_blocks(self, inode, block_index):
        for i in range(block_index, len(inode.blk_numbers)):
            if -1 != inode.blk_numbers[i]:
                interface.free_data_block(inode.blk_numbers[i])
                inode.blk_numbers[i] = -1
        return
    
    
    def find_block_size(self, inode, block_index):
        size_count = 0
        block = []
        block.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[block_index]))
        for ch in block:
            if ch == '\0':
                return size_count
            size_count += 1
        return size_count
    
    
    def write_blocks(self, inode, block_index, data_blocks):
        for block in data_blocks:
            block_number = interface.get_valid_data_block()
            inode.blk_numbers[block_index] = block_number
            interface.update_data_block(block_number, block)
        return
    
    
    def get_blocks_from_data(self, inode, data):
        data_blocks = []
        data_count = len(data)
        count = 0
        for i in range(0, len(data), config.BLOCK_SIZE):
            data_blocks.append(data[i : i + config.BLOCK_SIZE])

        print data_blocks
        return
    
    
    #FIND BLOCK NUMBER AND OFFSET IN THAT BLOCK BASED ON OFFSET AND LENGTH
    def find_block_and_offset(self, inode, offset, data):
        index = offset / config.BLOCK_SIZE
        if index >= len(inode.blk_numbers):
            return (-1, -1)
        
        offset_in_block = offset % config.BLOCK_SIZE
        return (index, offset_in_block)
    
    
    #ALLOCATE NEW BLOCKS FOR WRITE
    def allocate_new_blocks(self, data):
        blocks = []
        #Find the number of new blocks required. ALlocate new blocks
        num_of_blocks = len(data) / config.BLOCK_SIZE
        if len(data) % config.BLOCK_SIZE != 0: #Since division is floored, add 1 to correct it
            num_of_blocks += 1

        for i in range(num_of_blocks):
            blocks.append(interface.get_valid_data_block())
        return blocks
    
    
    #WRITES DATA TO BLOCKS PROVIDED
    def write_data_to_blocks(self, inode, blocks, inode_block_index, data):
        block_index = 0

        #Write data into alloted blocks. Also, update the list of blocks occupied in inode
        for i in range(0, len(data), config.BLOCK_SIZE):
            interface.update_data_block(blocks[block_index], data[i : i + config.BLOCK_SIZE])
            inode.blk_numbers[inode_block_index] = blocks[block_index]
            inode_block_index += 1
            block_index += 1
        return
    
    
    #CHECKS IF THE LENGTH PROVIDED EXCEEDS FILE SIZE
    def is_truncate_required(self, inode, data_length):
        num_blocks_available = 0
        for i in range(len(inode.blk_numbers)):
            if -1 == inode.blk_numbers[i]:
                break
        num_blocks_available = len(inode.blk_numbers) - i
        if data_length > (config.BLOCK_SIZE * num_blocks_available):
            return True
        return False
    
    #CHECKS IF THE OFFSET PROVIDED IN THE BLOCK IS A VALID INDEX FOR READ
    def is_offset_in_block_invalid(self, inode, block_index, offset_in_block):
        #Check if there are holes in existing blocks and new block
        for i in range(block_index):
            if inode.blk_numbers[i] == -1:
                return True
        #If the new data will be written from the start of a new block, then there are no gaps
        if offset_in_block == 0 or inode.blk_numbers[block_index] == -1:
            return False
        #If the previous element in the already stored data is NULL, then there are gaps between stored data and new data
        if inode.blk_numbers[block_index] != -1:
            stored_data = []
            stored_data.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[block_index]))
            if stored_data[offset_in_block - 1] == '\0':
                return True
            else:
                return False
        return True
    
     #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):
        #Check file type
        if False == inode.is_inode_type_file():
            print "ERROR: inode not a file"
            return inode
        block_index, offset_in_block = self.find_block_and_offset(inode, offset, data)
        #Check if the block_index is out of range
        if True == self.is_invalid_block_index(block_index):
            print "ERROR: Offset out of range"
            return inode
        #Check if the new data can be appended to already stored data. If there are gaps in between, print error
        if True == self.is_offset_in_block_invalid(inode, block_index, offset_in_block):
            print "ERROR: Invalid offset. Data in file not continuous"
            return inode
        stored_data = []
        #Copy the already stored data
        if False == self.is_block_empty(inode, block_index):
            stored_data.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[block_index]))

        #Erase blocks starting from block_number until the end
        self.empty_further_blocks(inode, block_index)

        final_data = []
        #Append data to already stored data
        if offset_in_block > 0:
            final_data.extend(stored_data[0:offset_in_block])
        
        data_len = len(final_data) + len(data)
        #Check if the entire data can fit into available memory blocks
        if True == self.is_truncate_required(inode, data_len):
            print "ERROR: Data more than file size. Data will be truncated"
            updated_data_len = self.get_max_file_size(inode) - offset
            data = data[:updated_data_len]
        
        #Append user data
        final_data.extend(data)
        
        #Allocate new blocks for the data
        blocks = self.allocate_new_blocks(final_data)
        #Store data into newly alloted blocks
        self.write_data_to_blocks(inode, blocks, block_index, final_data)
        #Update write time
        self.update_write_time(inode)
        
        return inode
    
    
    #RETURNS THE BLOCKS THAT NEED TO BE READ BASED ON OFFSET AND LENGTH
    def get_blocks_to_read(self, inode, offset, length):
        block_index = offset / config.BLOCK_SIZE
        offset_in_block = self.get_offset_in_block(offset)
        
        last_block = length / config.BLOCK_SIZE
        blocks = []
        #Holes can't be present in the middle
        for i in range(block_index, 1+block_index+last_block):
            if (len(inode.blk_numbers) <= i) or (-1 == inode.blk_numbers[i]):
                break
            blocks.append(inode.blk_numbers[i])
        return blocks
        
    #READS BLOCKS STARTING FROM offset_in_first_block IN FIRST BLOCK UNTIL offset_in_last_block IN THE LAST BLOCK
    def read_blocks(self, blocks, offset_in_first_block, offset_in_last_block):
        data = []
        first_block = []
        # no need to copy data from beginning in the last block, if there is only one block
        if len(blocks) == 1:
            data.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(blocks[0]))
            return "".join(data[offset_in_first_block:offset_in_last_block])
        
        first_block.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(blocks[0]))
        #Copy data from the offset position in first block
        data.extend(first_block[offset_in_first_block:])
        for i in range(1, len(blocks)-1):
            data.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(blocks[i]))
        last_block = []
        #Copy data upto length + offset in last block
        last_block.extend(interface.BLOCK_NUMBER_TO_DATA_BLOCK(blocks[len(blocks)-1]))
        data.extend(last_block[:offset_in_last_block])
        
        ret_data = "".join(data)
        return ret_data
    
    
    #IMPLEMENTS THE READ FUNCTION 
    def read(self, inode, offset, length):
        data_read = []
        if False == inode.is_inode_type_file():
            print "ERROR: inode not a file"
            return (inode, "")
        #Check if offset is within size of the file
        if True == self.is_invalid_read_offset(inode, offset):
            print "ERROR: Invalid offset for read"
            return (inode, "")
        
        if length == -1:
            length = len(inode.blk_numbers) * config.BLOCK_SIZE
        #Get block number of data from offset
        blocks = self.get_blocks_to_read(inode, offset, length)

        if not blocks:
            print "ERROR: Invalid blocks to read"
            return (inode, "")
        offset_in_first_block = self.get_offset_in_block(offset)
        offset_in_last_block = self.get_offset_in_block(offset_in_first_block + length)
        if (offset + length) > (len(blocks) * config.BLOCK_SIZE): 
            #print "ERROR: Data more than file size requested. Read data will be truncated"
            offset_in_last_block = (len(blocks) * config.BLOCK_SIZE)
        data_read = self.read_blocks(blocks, offset_in_first_block, offset_in_last_block)
        
        #Update file read time
        self.update_read_time(inode)
        
        return (inode, data_read)
