# Imports
import os
import socket
import subprocess
import threading
import time
from datetime import datetime, date
import pyautogui
import platform


def show_folder_content(fol_path):
    try:
        return os.listdir(fol_path)
    except OSError:
        return "An error has occurred while trying to open the folder, check the path!"


def open_file(file_path):
    try:
        subprocess.run(args=file_path)
        file = open(file_path, "r")
        file.close()
        return "The server has successfully opened the requested file!"
    except OSError:
        return "An error has occurred in opening the file, check the file path!"


def check_if_exists(username, password):
    username_list = read_username_list()
    flag = False
    for username_details in username_list:
        if username == username_details[0] and password == username_details[1]:
            flag = True
    return flag


def command_menu(server):
    server.send(bytes("Here are the commands:\n"
                      "'TIME' - Returns the current time in your computer\n"
                      "'NAME' - Returns the server's name\n"
                      "'EXIT' - Closes the connection to the server\n"
                      "'SCREEN_SHOT' - The server takes a screen shot and send it\n"
                      "'OPEN {path}' - The server tries to open the software and returns if it "
                      "was a success or a failure\n"
                      "'SHOW {folder path}' - The server returns the contents of the specified folder\n"
                      "'STOP_KEEP_ALIVE' - The server stops sending the status between you and the server\n",
                      "utf-8"))


def register_user(username, password):
    try:
        f = open(
            "C:/Users/talsh/OneDrive/Desktop/Flash Drive Backup/Amal B Computer Programming 14th "
            "Grade/Golan/avodatHagasha/Server Files/usernames.txt",
            "a+")
        f.write(f"{username} {password}\n")
        f.close()
    except OSError as e:
        print(e.strerror)


def get_username_information(data_string):
    user_obj = {
        'type': '',
        'information': []
    }
    if data_string.startswith('CONNECT: '):
        user_obj['type'] = 'CONNECT'
        simplified_data = data_string[9:]
        if simplified_data.count(" ") == 1:
            username_information = simplified_data.rsplit(' ')
            user_obj['information'] = username_information
        else:
            return "You did not enter correct information"
    elif data_string.startswith("REGISTER: "):
        user_obj['type'] = 'REGISTER'
        simplified_data = data_string[10:]
        if simplified_data.count(" ") == 1:
            username_information = simplified_data.rsplit(' ')
            user_obj['information'] = username_information
        else:
            return "You did not enter correct information"
    else:
        return "You did not enter correct information"
    return user_obj


def username_obj(line):
    username = ''
    password = ''
    reached_empty_space = False
    for ch in line:
        if ch == ' ':
            reached_empty_space = True
            continue
        if ch == '\n':
            break
        if reached_empty_space:
            password += ch
        else:
            username += ch
    return [username, password]


def read_username_list():
    username_list = []
    mutex.acquire()
    try:
        f = open(
            "C:/Users/talsh/OneDrive/Desktop/Flash Drive Backup/Amal B Computer Programming 14th "
            "Grade/Golan/avodatHagasha/Server Files/usernames.txt",
            "r")
        lines = f.readlines()
        for line in lines:
            username_list.append(username_obj(line))
    except OSError as e:
        print(f"Error: {e.strerror}")
    finally:
        mutex.release()
    return username_list


def is_keep_alive(server, keep_alive=True):
    now = time.time()
    try:

        while keep_alive and time.time() - now < 10:
            server.send(bytes("Connected...", "utf-8"))
            data = server.recv(1024).decode("utf-8")
            if data == "Received...":
                now = time.time()
                time.sleep(5)
            else:
                raise InterruptedError
        raise InterruptedError
    except (InterruptedError, ConnectionAbortedError, ConnectionResetError, OSError):
        time.sleep(10)
        server.send(bytes("Connection to remote expired", "utf-8"))


def handle_connection(this_socket):
    this_socket.send(bytes("Welcome to the server!\n", "utf-8"))
    this_socket.send(bytes("Please enter Username and Password using the following Syntax's:\n"
                           "For Connection: 'CONNECT: {username} {password}'\n"
                           "For Registration: 'REGISTER: {username} {password}'\n", "utf-8"))

    # Prints the registered users
    print("File Content:")
    print(read_username_list())  # read_username_list returns a list which each item is its own list containing 2
    # strings: username and password

    # data contains initial string sent from the user such as "CONNECT: talsh 356930tal"
    data = this_socket.recv(1024).decode("utf-8")
    data = data.strip()
    if data != "":
        print(data)
    user_information = get_username_information(data)  # user_information contains the username and password the user
    # sent as an object { 'type' : {connection_type}, 'information': [username, password]}
    print(user_information)
    if user_information != "You did not enter correct information":
        if user_information['type'] == "CONNECT":
            if check_if_exists(user_information['information'][0], user_information['information'][1]):
                this_socket.send(bytes("Connection successful, you're logged in", "utf-8"))
            else:
                this_socket.send(bytes("Bad Connection Parameters", "utf-8"))
                this_socket.shutdown(socket.SHUT_RDWR)
                this_socket.close()
        else:
            register_user(user_information['information'][0], user_information['information'][1])
            this_socket.send(
                bytes("User has been registered successfully!\n"
                      "You have been logged in automatically", "utf-8"))
    else:
        this_socket.send(bytes(user_information, "utf-8"))
        this_socket.shutdown(socket.SHUT_RDWR)
        this_socket.close()

    command_menu(this_socket)  # Shows commands to client
    user_input = this_socket.recv(1024).decode("utf-8")  # user_input is what the command the client sent

    screen_shot_count = 0

    while True:
        if user_input == "TIME":
            today = date.today().strftime("%d/%m/%Y")
            current_time = datetime.now().strftime("%H:%M:%S")
            this_socket.send(bytes(f"Today's date: {today}.\n"
                                   f"Current time: {current_time}", "utf-8"))
        if user_input == "NAME":
            this_socket.send(bytes(f"Peer name: {this_socket.getpeername()}\n"
                                   f"Socket name: {this_socket.getsockname()}\n"
                                   f"Platform name: {platform.uname()[1]}", "utf-8"))
        if user_input == "EXIT":
            this_socket.send(bytes("Bye bye!", "utf-8"))
            this_socket.shutdown(socket.SHUT_RDWR)
            this_socket.close()
            break
        if user_input == "SCREEN_SHOT":
            this_socket.send(bytes("Sending screen shot...", "utf-8"))
            # Checks if the directory exists, otherwise creates it
            if not os.path.isdir("./screen_shots"):
                os.mkdir("./screen_shots")
            pic = pyautogui.screenshot()
            # Saves the screen shot
            pic.save(f"./screen_shots/screen_shot_{screen_shot_count}.png")
            pic.show()
            # Opens the screen shot and reads it
            img = open(f"./screen_shots/screen_shot_{screen_shot_count}.png", "rb")
            image_data = img.read()
            image_size = len(image_data)
            # Sends the client the image size
            this_socket.send(bytes(f"Size {image_size}", "utf-8"))
            answer = this_socket.recv(4096).decode("utf-8")
            print(f"Answer = {answer}")
            # Sends image to client
            if answer == 'GOT SIZE':
                this_socket.sendall(image_data)

                # Checks confirmation from client
                answer = this_socket.recv(4096).decode("utf-8")
                print(f"answer = {answer}")

                if answer == "GOT IMAGE":
                    print("Finished sending!")
            img.close()
            screen_shot_count += 1
        if user_input.find('OPEN') != -1:
            path = user_input[5:]  # user_input[5:] is supposed to include "{path}"
            output = open_file(path)  # need to write get_file function that gets a file's path and
            # tries to open it, returns a proper message if successful or not
            this_socket.send(bytes(output, "utf-8"))
        if user_input.find('SHOW') != -1:
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
        if user_input == "STOP_KEEP_ALIVE":
            is_keep_alive(s_keep_alive_socket, False)
            time.sleep(20)
        try:
            command_menu(this_socket)
            user_input = this_socket.recv(1024).decode("utf-8")
            user_input = user_input.strip()
        except (OSError, ConnectionAbortedError, ConnectionResetError, InterruptedError):
            break


# Defining mutex object for allowing multiple threads access the users file
mutex = threading.Lock()

# Defining out socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 2222))
s.listen(5)

s_keep_alive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_keep_alive.bind(('', 3333))
s_keep_alive.listen(5)

while True:
    client_socket, address = s.accept()
    print(f"Connection from {address} has been established!")
    thread2 = threading.Thread(target=handle_connection, args=(client_socket,))
    thread2.start()

    s_keep_alive_socket, s_keep_alive_address = s_keep_alive.accept()
    print(f"Connection from {s_keep_alive_address} has been established!")
    thread3 = threading.Thread(target=is_keep_alive, args=(s_keep_alive_socket, ))
    thread3.start()
