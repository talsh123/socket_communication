# Imports
import os
import socket
import threading


def check_user_input(user_input):
    if user_input != "":
        return True
    return False


def is_alive(keep_alive_socket):
    while True:
        keep_alive_data = keep_alive_socket.recv(1024).decode("utf-8")
        if keep_alive_data == "Connected...":
            keep_alive_socket.send(bytes("Received...", "utf-8"))
        elif keep_alive_data == "Connection to remote expired":
            print(keep_alive_data)
            keep_alive_socket.shutdown(socket.SHUT_RDWR)
            keep_alive_socket.close()
            break
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    exit(0)


# Defining out socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.0.19', 2222))

keep_alive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive.connect(('10.0.0.19', 3333))

thread2 = threading.Thread(target=is_alive, args=(keep_alive, ), daemon=True)
thread2.start()

screen_shot_count = 0

while True:
    try:
        data = s.recv(1024).decode("utf-8")
        if not data:
            break
        if data == "Bye bye!" or data == "You did not enter correct information" or data == "Bad Connection Parameters":
            print(data)
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            exit(0)
        elif data.find("For Registration") != -1 or data.find("STOP_KEEP_ALIVE") != -1:  # If the server shows the
            # commands or asks the user for information
            print(data)
            my_input = input()
            if check_user_input(my_input):
                s.sendall(bytes(my_input, "utf-8"))
            else:
                print("You need to enter a valid value")
                s.shutdown(socket.SHUT_RDWR)
                s.close()
        elif data == "Sending screen shot...":
            # Checking if the directory exists, otherwise creating it
            if not os.path.isdir(f"./{socket.gethostname()}"):
                os.mkdir(f"./{socket.gethostname()}")
            # Receiving data
            data = s.recv(4096).decode("utf-8")
            # Checks if image size received
            if data.startswith("Size"):
                tmp = data.rsplit(' ')
                img_size = tmp[1]
                print("got size")
                # Sends "GOT SIZE" to server
                s.send(bytes("GOT SIZE", "utf-8"))

                # Opens the file and starts writing into it
                f = open(f"./{socket.gethostname()}/screen_shot_{screen_shot_count}.png", "wb+")
                data = s.recv(int(img_size))
                if not data:
                    f.close()
                f.write(data)
                f.close()

                s.send(bytes("GOT IMAGE", "utf-8"))
                screen_shot_count += 1
                print("File received and saved!")
        else:
            print(data)
    except (OSError, ConnectionResetError, ConnectionAbortedError, InterruptedError):
        break
