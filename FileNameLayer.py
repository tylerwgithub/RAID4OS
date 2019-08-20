'''
THIS MODULE ACTS LIKE FILE NAME LAYER AND PATH NAME LAYER (BOTH) ABOVE INODE LAYER.
IT RECIEVES INPUT AS PATH (WITHOUT INITIAL '/'). THE LAYER IMPLEMENTS LOOKUP TO FIND INODE NUMBER OF THE REQUIRED DIRECTORY.
PARENTS INODE NUMBER IS FIRST EXTRACTED BY LOOKUP AND THEN CHILD INODE NUMBER BY RESPECTED FUNCTION AND BOTH OF THEM ARE UPDATED
'''
import InodeNumberLayer

#HANDLE OF INODE NUMBER LAYER
interface = InodeNumberLayer.InodeNumberLayer()

class FileNameLayer():

    #PLEASE DO NOT MODIFY
    #RETURNS THE CHILD INODE NUMBER FROM THE PARENTS INODE NUMBER
    def CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(self, childname, inode_number_of_parent):
        inode = interface.INODE_NUMBER_TO_INODE(inode_number_of_parent)
        if not inode: 
            print("Error FileNameLayer: Lookup Failure!")
            return -1
        if inode.type == 0:
            print("Error FileNameLayer: Invalid Directory!")
            return -1
        if childname in inode.directory: return inode.directory[childname]
        print("Error FileNameLayer: Lookup Failure!")
        return -1

    #PLEASE DO NOT MODIFY
    #RETUNS THE PARENT INODE NUMBER FROM THE PATH GIVEN FOR A FILE/DIRECTORY 
    def LOOKUP(self, path, inode_number_cwd):   
        name_array = path.split('/')
        if len(name_array) == 1: return inode_number_cwd
        else:
            child_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(name_array[0], inode_number_cwd)
            if child_inode_number == -1: return -1
            return self.LOOKUP("/".join(name_array[1:]), child_inode_number)

    #PLEASE DO NOT MODIFY
    #MAKES NEW ENTRY OF INODE
    def new_entry(self, path, inode_number_cwd, type):
        import time
        start_time = time.time()
        if path == '/': #SPECIAL CASE OF INITIALIZING FILE SYSTEM
            interface.new_inode_number(type, inode_number_cwd, "root")
            #print ("Time to create root: "), (time.time() - start_time)
            return True
        parent_inode_number = self.LOOKUP(path, inode_number_cwd)
        parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
        childname = path.split('/')[-1]
        if not parent_inode: return -1
        if childname in parent_inode.directory:
            print("Error FileNameLayer: File already exists!")
            return -1
        child_inode_number = interface.new_inode_number(type, parent_inode_number, childname)  #make new child
        if child_inode_number != -1:
            parent_inode.directory[childname] = child_inode_number
            interface.update_inode_table(parent_inode, parent_inode_number)
        #print ("Time to create file: "), (time.time() - start_time)


    #IMPLEMENTS READ
    def read(self, path, inode_number_cwd, offset, length):
        '''WRITE YOUR CODE HERE'''
        parent_inode_number = self.LOOKUP(path, inode_number_cwd)
        childname = path.split('/')[-1]
        if len(childname) == 0:
            print("Error FileNameLayer: Invalid file!")
            return -1
        #Find the inode number of the file and get data from InodeLayer
        inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(childname, parent_inode_number)
        if inode_number == -1:
            return -1
        return interface.read(inode_number, offset, length, parent_inode_number)
    
    
    #IMPLEMENTS WRITE
    def write(self, path, inode_number_cwd, offset, data):
        '''WRITE YOUR CODE HERE'''
        parent_inode_number = self.LOOKUP(path, inode_number_cwd)
        childname = path.split('/')[-1]
        if len(childname) == 0:
            print("Error FileNameLayer: Invalid file!")
            return -1
        #Find inode number of the file and pass the data to InodeLayer
        inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(childname, parent_inode_number)
        if inode_number == -1:
            return -1
        return interface.write(inode_number, offset, data, parent_inode_number)
    
    #Print all files and directories
    def print_files_in_inode(self, inode):
        if not inode.directory:
            print "Empty directory"
            return
        for key, val in inode.directory.items():
            print "Name : ", key, " :: inode number : ", val
        return
    
    #Print all files and directories in a given directory path
    def print_files_inodes_in_path(self, path, inode_number_cwd):
        inode_number = self.LOOKUP(path, inode_number_cwd)
        if not interface.is_dir(inode_number):
            return
        inode = interface.INODE_NUMBER_TO_INODE(inode_number)
        print "Dir : ", inode.name
        for dire in inode.directory:
            dir_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(dire, inode_number)
            dir_inode = interface.INODE_NUMBER_TO_INODE(dir_inode_number) 
            if not dir_inode:
                print "Invalid file/directory!"
                return -1
            
            self.print_files_in_inode(dir_inode)
            
        return
    
    #HARDLINK
    def link(self, old_path, new_path, inode_number_cwd):
        '''WRITE YOUR CODE HERE'''
        #If a link to root is being created
        if old_path == "":
            file_inode_number = inode_number_cwd
            parent_inode_number = inode_number_cwd
        else:
            parent_inode_number = self.LOOKUP(old_path, inode_number_cwd)
            parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number)
            if not parent_inode:
                print("Error FileNameLayer: Invalid file directory!")
                return -1
            filename = old_path.split('/')[-1]
            if len(filename) == 0:
                print("Error FileNameLayer: Invalid file/dir name!")
                return -1
            #Check if the file/directory exists
            if filename not in parent_inode.directory:
                print("Error FileNameLayer: File/directory not found! : "), filename
                return -1
            #Get file inode number and add it into the link's directory
            file_inode_number = parent_inode.directory[filename]
            
        linkname = new_path.split('/')[-1]
        if len(linkname) == 0:
            print("Error FileNameLayer: Invalid linkname!")
            return -1
        #Check if the link will be placed in root. This case is valid for mv function only
        #For all other calls '/' is stripped from the path
        if new_path[0] == '/':
            link_parent_inode_number = inode_number_cwd
        else:
            link_parent_inode_number = self.LOOKUP(new_path, inode_number_cwd)
        link_parent_inode = interface.INODE_NUMBER_TO_INODE(link_parent_inode_number)
        
        if not link_parent_inode:
            print("Error FileNameLayer: Invalid link directory!")
            return -1
        #Check if a file/directory by linkname already exists
        if linkname in link_parent_inode.directory:
            print("Error FileNameLayer: Name used for link already exists! : "), linkname
            return -1
        link_parent_inode.directory[linkname] = file_inode_number
        #Update the changes to inode table
        interface.update_inode_table(link_parent_inode, link_parent_inode_number)
        
        return interface.link(file_inode_number, parent_inode_number)
    
    
    #REMOVES THE FILE/DIRECTORY
    def unlink(self, path, inode_number_cwd):
        if path == "": 
            print("Error FileNameLayer: Cannot delete root directory!")
            return -1
        '''WRITE YOUR CODE HERE'''
        parent_inode_number = self.LOOKUP(path, inode_number_cwd)
        parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number)
        if not parent_inode:
            print("Error FileNameLayer: Invalid directory!")
            return -1
        linkname = path.split('/')[-1]
        if len(linkname) == 0:
            print("Error FileNameLayer: Invalid linkname!")
            return -1
        #If the link is not found, return error
        if linkname not in parent_inode.directory:
            print("Error FileNameLayer: Link not found!")
            return -1
        link_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(linkname, parent_inode_number)
        #If the remove is requested for directory, do not remove it before it's empty
        link_inode = interface.INODE_NUMBER_TO_INODE(link_inode_number)
        if True == interface.is_dir(link_inode_number):
            #If there are more than 2 links to a directory, allow removal of link
            #if there are no contents in the directory, go ahead, delete it
            if link_inode.links == 2 and link_inode.directory:
                print("Error FileNameLayer: Only empty directories can be deleted!")
                return -1
        #Remove the entry from link's directory 
        parent_inode.directory.pop(linkname, None)
        interface.update_inode_table(parent_inode, parent_inode_number)
        return interface.unlink(link_inode_number, parent_inode_number) 



    #MOVE
    def mv(self, old_path, new_path, inode_number_cwd):
        '''WRITE YOUR CODE HERE'''
        if old_path == "": 
            print("Error FileNameLayer: Cannot move root directory!")
            return -1
        #If the move path is root
        if new_path == "":
            new_path = "/"
            #Root inode number passed from AbsolutePathLayer
            new_parent_inode_number = inode_number_cwd
        
        else:
            #Find the parent directory in for the new location
            if new_path[-1] != '/':
                new_path = new_path + '/'
            new_parent_inode_number = self.LOOKUP(new_path, inode_number_cwd)
        
        old_parent_inode_number = self.LOOKUP(old_path, inode_number_cwd)
        old_parent_inode = interface.INODE_NUMBER_TO_INODE(old_parent_inode_number)
        new_parent_inode = interface.INODE_NUMBER_TO_INODE(new_parent_inode_number)
        
        if not old_parent_inode or not new_parent_inode:
            print("Error FileNameLayer: Invalid directories for mv!")
            return -1
        
        if not interface.is_dir(old_parent_inode_number) or not interface.is_dir(new_parent_inode_number):
            print("Error FileNameLayer: Invalid directories for mv!")
            return -1
        
        old_name = old_path.split('/')[-1]
        if len(old_name) == 0:
            print ("Error FileNameLayer: Invalid file/directory!")
            return -1
        
        inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(old_name, old_parent_inode_number)
        if inode_number == -1:
            print ("Error FileNameLayer: Invalid file/directory!")
            return -1
        #if the given path is a directory, move all contents
        if interface.is_dir(inode_number):
            print("Moving directory and its contents")
        #Enter a file/directory with the same name in the new directory i.e make a link to the old inode 
        #Delete the old entry
        new_name = old_name
        #Check if the new name already exists in the directory
        if new_name in new_parent_inode.directory:
            print("Error FileNameLayer: File/directory name already exists! : "), new_name
            return -1
        new_path = new_path + new_name
        #If a directory is being moved to another directory inside it
        if len(new_path) >= len(old_name) and old_path == new_path[:len(old_name)]:
            print ("Error FileNameLayer: Invalid nesting of directories!")
            return -1
        #Link to the new path
        self.link(old_path, new_path, inode_number_cwd)
        #Unlink from the old path
        self.unlink(old_path, inode_number_cwd)
        
        return 
