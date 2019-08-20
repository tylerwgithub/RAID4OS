import FileSystem
import config

interface = FileSystem.FileSystemOperations()


def Initialize():
	print "Number of Data Servers : ", config.NUM_OF_SERVERS
	delay = 0
	try:
		delay = int(raw_input("Enter delay value : "))
	except Exception as err:
		print err
		print "Delay defaulted to ", delay
	config.SLEEP_TIME = delay
	while (True):
		try:
			startpoint = raw_input("Please enter 4 digit starting port number : ")
   			if len(startpoint) == 4:
   				config.SERVER_PORT_BEGIN = int(startpoint)
   				raw_input("Press enter after starting the servers : ")
   				FileSystem.Initialize_My_FileSystem()
   				break
   			print ("The length is not 4!")
		except ValueError:
   			print("That's not an Integer!")
   	return
   			
   			
   			
def main():
	while (True):
		input = raw_input("$ ")
		input_array = input.split(' ')
		if len(input_array) > 0:
			if input_array[0] == "exit":
				break
			if input_array[0] == "mkdir":
				mkdir(input_array)
			if input_array[0] == "create":
				create(input_array)
			if input_array[0] == "write":
				write(input_array)
			if input_array[0] == "read":
				read(input_array)
			if input_array[0] == "rm":
				rm(input_array)
			if input_array[0] == "mv":
				mv(input_array)
			if input_array[0] == "link":
				link(input_array)
			if input_array[0] == "status":
				print status()
	return


def mkdir(input_array):
	if len(input_array) < 2:
		print "Incorrect input"
		return
	try:
		interface.mkdir(input_array[1])
	except Exception as error:
		print error
	return
	


#CREATE FILE
def create(input_array):
	if len(input_array) < 2:
		print "Incorrect input"
		return
	try:
		interface.create(input_array[1])
	except Exception as error:
		print error
	return

#WRITE TO FILE
def write(input_array):
	if len(input_array) < 4:
		print "Incorrect input"
		return
	try:
		offset = int(input_array[2])
		data = ' '.join(input_array[3:])
		interface.write(input_array[1], data, offset)
	except Exception as error:
		print error
  	return

#READ
def read(input_array):
	offset = 0
	size = -1
	try:
		if len(input_array) > 2:
			offset = int(input_array[2])
		if len(input_array) > 3:
			size = int(input_array[3])
		return interface.read(input_array[1], offset, size)
	except Exception as error:
		print error
	return


#DELETE
def rm(input_array):
	if len(input_array) < 2:
		print "Incorrect input"
		return
	try:
		interface.rm(input_array[1])
	except Exception as error:
		print error
	return

#MOVING FILE
def mv(input_array):
	if len(input_array) < 3:
		print "Incorrect input"
		return
	try:
		interface.mv(input_array[1], input_array[2])
	except Exception as error:
		print error
	return

def link(input_array):
	if len(input_array) < 3:
		print "Incorrect input"
		return
	try:
		interface.link(input_array[1], input_array[2])
	except Exception as error:
		print error
	return
	
#CHECK STATUS
def status():
	return (interface.status())

if __name__ == "__main__":

	Initialize()
	main()
	


