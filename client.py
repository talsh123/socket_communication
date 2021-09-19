# Imports
import socket

# Define socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.0.32', 2222))

while True:
    data = s.recv(1024).decode("utf-8")
    if not data:
        break
    elif data.find("") != -1 or data.find('For Registration') != -1 or data.find('Here') != -1 or data.find('An error has occurred') != -1 or data.find('Credentials are not in the correct format') != -1 or data.find('Your credentials are incorrect, please try again') != -1:
        print(data)
        my_input = input()
        if my_input != "":
            s.sendall(bytes(my_input, "utf-8"))
        else:
            print("You need to enter a valid value")
    else:
        print(data)