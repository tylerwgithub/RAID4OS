#Total blocks must be greater than block size
#Inode size must be less than Block size 
#Min size of file name is 5


TOTAL_NO_OF_BLOCKS = 1024
BLOCK_SIZE = 512
MAX_NUM_INODES = 32
INODE_SIZE = 128
MAX_FILE_NAME_SIZE = 8


# Project definitions
NUM_OF_SERVERS = 5
NUM_OF_DATA_SERVERS = NUM_OF_SERVERS - 1
SERVER_PORT_BEGIN = 8000
VIRTUAL_BLOCK_START = 10
REDUNDANCY_COUNT = 2
DATA_BLOCK_1 = 0
DATA_BLOCK_2 = 1
PARITY_BLOCK = 2


SOCKET_TIMEOUT = 5
