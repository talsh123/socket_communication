# Imports
import os
import socket
from datetime import datetime, date
import pyautogui
import platform

# Close the connection and stop the program
def close_connection(server):
    server.shutdown(socket.SHUT_RDWR)
    server.close()
    quit()

# Return the files included in the given path, otherwise return None
def show_folder_content(path, server):
    try:
        for item in os.listdir(path):
            server.send(bytes(f'{item}\n', 'utf-8'))
    except OSError:
        server.send(bytes('An error has occurred\n', 'utf-8'))
        return None


# Try to open a file given the file path
def open_file(file_path, server):
    try:
        file = open(file_path, "r")
        file.close()
        server.send(bytes('The server has successfully opened the file\n', 'utf-8'))
    except OSError:
        server.send(bytes('An error has occurred\n', 'utf-8'))


# Send the commands to the connected client
def command_menu(server):
    server.send(bytes("""
    Here are the commands:
    'time' - Returns the current time in your computer
    'name' - Returns the server's name
    'exit' - Closes the connection to the server
    'screen_shot' - The server takes a screen shot and send it
    'open {path}' - The server tries to open the software and returns if it was a success or a failure
    'show {folder path}' - The server returns the contents of the specified folder
    """, 'utf-8'))


# Register a new user, write the credentials in usernames.txt
def register_user(username, password, server):
    try:
        f = open(os.getcwd() + './usernames.txt', 'a+')
        f.write(f"{username} {password}\n")
        f.close()
        server.send(bytes('User has successfully registered', 'utf-8'))
    except OSError as e:
        server.send(bytes('An error has occurred\n', 'utf-8'))


# Check if the user is connecting or registering and returns the data
def get_user_input(user_input, server):
    err = False
    data = {
        'type': '',
        'credentials': []
    }
    if user_input.startswith('connect: '):
        data['type'] = 'connect'
        if user_input[9:].count(" ") == 1:
            data['credentials'] = user_input[9:].split()
            return data
        else:
            err = True
    elif user_input.startswith("register: "):
        data['type'] = 'register'
        if user_input[10:].count(" ") == 1:
            data['credentials'] = user_input[10:].split()
            return data
        else:
            err = True
    else:
        err = True
    if err:
        server.send(bytes("Credentials are not in the correct format\n", "utf-8"))


# Check if the given credentials are correct as written in the usernames.txt file
def check_credentials(username, password, server):
    try:
        f = open(os.getcwd() + './usernames.txt', 'r')
        lines = f.readlines()
        for line in lines:
            if line.split()[0] == username and line.split()[1] == password:
                f.close()
                server.send(bytes('Credentials are correct\n', 'utf-8'))
                return True
        f.close()
        return False
    except OSError:
        server.send(bytes('An error has occurred\n', 'utf-8'))

# Main function which handle the user input and call other function accordingly
def handle_connection(this_socket):
    # Getting user credentials
    this_socket.send(bytes("""
    Welcome to the server!
    Please enter Username and Password using the following Syntax:
    For Connection: 'connect: {username} {password}'
    For Registration: 'register: {username} {password}'
    """, 'utf-8'))

    # Get user input
    user_input = this_socket.recv(1024).decode("utf-8")
    user_input = user_input.strip()

    # Get the user credentials
    user_credentials = get_user_input(user_input, this_socket)
    # If the user wish to connect
    if user_credentials['type'] == "connect":
        # Check if the user credentials are correct
        if check_credentials(user_credentials['credentials'][0].strip(), user_credentials['credentials'][1].strip(), this_socket):
            this_socket.send(bytes("Connection successful, you're logged in", "utf-8"))
        else:
            this_socket.send(bytes("Your credentials are incorrect, please try again", "utf-8"))
    elif user_credentials['type'] == 'register':
        register_user(user_credentials['credentials'][0].strip(), user_credentials['credentials'][1].strip(), this_socket)

    # Show commands to client and get user input
    command_menu(this_socket)
    user_input = this_socket.recv(1024).decode("utf-8")  

    while True:
        if user_input == "time":
            today = date.today().strftime("%d/%m/%Y")
            current_time = datetime.now().strftime("%H:%M:%S")
            this_socket.send(bytes(f"Today's date: {today}\n"
            f"Current time: {current_time}\n", "utf-8"))
        elif user_input == "name":
            this_socket.send(bytes(f"Peer name: {this_socket.getpeername()}\n"
            f"Socket name: {this_socket.getsockname()}\n"
            f"Platform name: {platform.uname()[1]}\n", "utf-8"))
        elif user_input == "exit":
            close_connection(this_socket)
        elif user_input == "screen_shot":
            # Check if the directory exists, otherwise creates it
            if not os.path.isdir("./screen_shots"):
                os.mkdir("./screen_shots")
            pic = pyautogui.screenshot()
            # Save the screen shot
            pic.save("./screen_shots/screen_shot.png")
            # Opens the screen shot and reads it
            img = open(f"./screen_shots/screen_shot.png", "rb")
            image_user_input = img.read()
            # Sends image to client
            this_socket.sendall(image_user_input)
            # Checks confirmation from client
            answer = this_socket.recv(4096).decode("utf-8")
            if answer == "got image":
                img.close()
        elif user_input.find('open') != -1:
            path = user_input[5:]
            open_file(path, this_socket)
        elif user_input.find('show') != -1:
            folder_path = user_input[5:]
            show_folder_content(folder_path, this_socket)
        try:
            command_menu(this_socket)
            user_input = this_socket.recv(1024).decode("utf-8")
            user_input = user_input.strip()
        except (OSError, ConnectionAbortedError, ConnectionResetError, InterruptedError):
            break


# Defining out socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 2222))
s.listen(5)

# Infinite look checking for 
while True:
    client_socket, address = s.accept()
    print(f"Connection from {address} has been established!")
    handle_connection(client_socket)