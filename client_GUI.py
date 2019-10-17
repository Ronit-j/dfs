import sys
import new_lib
from datetime import datetime
from time import gmtime, strftime
import copy

file_version_map = {}
client_id = strftime("%Y%m%d%H%M%S", gmtime())


def main():

    print ("\n")
    new_lib.instructions()

    client_input = sys.stdin.readline()

def client_write(text, filename):
    global file_version_map, client_id
    print("write file version map")
    print(file_version_map)
    client_input = "<write> " + filename
    if "<write>" in client_input:
        while not new_lib.check_valid_input(client_input):       # error check the input
             client_input = sys.stdin.readline()

        filename = client_input.split()[1]      # get the filename from the input
        response = new_lib.handle_write(filename, client_id, file_version_map, text)    # handle the write request
        if response == False:
            print("File unlock polling timeout...")
            print("Try again later...")
        print ("Exiting <write> mode...\n")


def client_read(filename):
    global file_version_map, client_id
    print("read file version map")
    print(file_version_map)
    client_input="<read> " + filename
    if "<read>" in client_input:
        #while not new_lib.check_valid_input(client_input):    # error check the input
        #     client_input = sys.stdin.readline()

        filename = client_input.split()[1]   # get file name from the input
        read=new_lib.handle_read(filename, file_version_map, client_id)        # handle the read request
        print("Exiting <read> mode...\n")
        print(read)
        return copy.deepcopy(read);

def client_list(client_input="<list>"):
    global file_version_map, client_id
    if "<list>" in client_input:
        client_socket = new_lib.create_socket()
        list=new_lib.send_directory_service(client_socket, "", "", True)
        client_socket.close()
        return list;
    #if "<create>" in client_input:
    #    while not new_lib.check_valid_input(client_input):       # error check the input
    #         client_input = sys.stdin.readline()
    #    filename = client_input.split()[1]
    #    new_lib.create_file(filename)

def client_instructions(client_input="<instructions>"):
    global file_version_map, client_id
    if "<instructions>" in client_input:
        new_lib.instructions()


def client_quit(client_input="<quit>"):
    global file_version_map, client_id
    if "<quit>" in client_input:
        print("Exiting application...")
        sys.exit()




if __name__ == "__main__":
    main()
