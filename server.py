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

# List the files included in the given path
def show_folder_content(path):
    try:
        return os.listdir(path)
    except OSError:
        return "An error has occurred trying to open the folder"


# Open a file, given the file path
def open_file(file_path):
    try:
        file = open(file_path, "r")
        file.close()
        return "The server has successfully opened the file!"
    except OSError:
        return "An error has occurred trying to open the file"


# Send the commands to the connected client
def command_menu(server):
    server.send(bytes("""
    Here are the commands:
    'time' - Returns the current time in your computer
    'name' - Returns the server's name
    'exit' - Closes the connection to the server
    'screen_shot' - The server takes a screen shot and send it
    'open {path}' - The server tries to open the software and returns if it 
    was a success or a failure
    'show {folder path}' - The server returns the contents of the specified folder
    """, "utf-8"))


# Register a new user, writing the credentials in usernames.txt
def register_user(username, password):
    try:
        f = open(os.getcwd() + './usernames.txt', 'a+')
        f.write(f"{username} {password}\n")
        f.close()
    except OSError as e:
        print(e.strerror)


# Check if the user us connecting or registering and returns the data
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
    if err:
        server.send(bytes("You did not enter credentials in the correct format\n", "utf-8"))
        close_connection(server)


# Check if the given credentials are correct as written in the usernames.txt file
def check_credentials(username, password):
    try:
        f = open(os.getcwd() + './usernames.txt', 'r')
        lines = f.readlines()
        for line in lines:
            if line.split()[0] == username and line.split()[1] == password:
                f.close()
                return True
        f.close()
        return False
    except OSError as e:
        print(f"Error: {e.strerror}")

# Main function which handle the user input and call other function accordingly
def handle_connection(this_socket):
    # Getting user credentials
    this_socket.send(bytes("""
    Welcome to the server!
    Please enter Username and Password using the following Syntax's:
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
        if check_credentials(user_credentials['credentials'][0].strip(), user_credentials['credentials'][1].strip()):
            this_socket.send(bytes("Connection successful, you're logged in", "utf-8"))
        else:
            this_socket.send(bytes("Your credentials are wrong, please try again", "utf-8"))
            close_connection(this_socket)
    elif user_credentials['type'] == 'register':
        register_user(user_credentials['credentials'][0], user_credentials['credentials'][1])
        this_socket.send(
            bytes("User has been registered successfully!\n", "utf-8"))
    else:
        close_connection(this_socket)

    # Show commands to client and get user input
    command_menu(this_socket)
    user_input = this_socket.recv(1024).decode("utf-8")  

    screen_shot_count = 0

    while True:
        if user_input == "time":
            today = date.today().strftime("%d/%m/%Y")
            current_time = datetime.now().strftime("%H:%M:%S")
            this_socket.send(bytes(f"Today's date: {today}.\n"
                                   f"Current time: {current_time}\n", "utf-8"))
        if user_input == "name":
            this_socket.send(bytes(f"Peer name: {this_socket.getpeername()}\n"
                                   f"Socket name: {this_socket.getsockname()}\n"
                                   f"Platform name: {platform.uname()[1]}\n", "utf-8"))
        if user_input == "exit":
            close_connection(this_socket)
            break
        if user_input == "screen_show":
            this_socket.send(bytes("Sending screen shot...", "utf-8"))
            # Check if the directory exists, otherwise creates it
            if not os.path.isdir("./screen_shots"):
                os.mkdir("./screen_shots")
            pic = pyautogui.screenshot()
            # Saves the screen shot
            pic.save(f"./screen_shots/screen_shot_{screen_shot_count}.png")
            pic.show()
            # Opens the screen shot and reads it
            img = open(f"./screen_shots/screen_shot_{screen_shot_count}.png", "rb")
            image_user_input = img.read()
            image_size = len(image_user_input)
            # Sends the client the image size
            this_socket.send(bytes(f"Size {image_size}", "utf-8"))
            answer = this_socket.recv(4096).decode("utf-8")
            # Sends image to client
            if answer == 'GOT SIZE':
                this_socket.sendall(image_user_input)

                # Checks confirmation from client
                answer = this_socket.recv(4096).decode("utf-8")

                if answer == "GOT IMAGE":
                    print("Finished sending!")
            img.close()
            screen_shot_count += 1
        if user_input.find('open') != -1:
            path = user_input[5:]  # user_input[5:] is supposed to include "{path}"
            output = open_file(path)  # need to write get_file function that gets a file's path and
            # tries to open it, returns a proper message if successful or not
            this_socket.send(bytes(output, "utf-8"))
        if user_input.find('show') != -1:
            folder_path = user_input[5:]
            content = show_folder_content(folder_path)  # need to write show_folder_content function that returns the
            if content == "An error has occurred while trying to open the folder, check the path!":
                this_socket.send(bytes(content, "utf-8"))
            else:
                # folder content that's given
                sub_folder_str = ''
                for sub_folder in content:
                    sub_folder_str += f"{sub_folder}\n"
                this_socket.send(bytes(sub_folder_str, "utf-8"))
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