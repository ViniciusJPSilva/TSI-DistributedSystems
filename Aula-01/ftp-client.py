import socket

HOST = "127.0.0.1"
PORT = 14000

FILE_PATH = "./img.jpg"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))

    print("Conectado ao servidor.")

    with open(FILE_PATH,"rb") as file:
        while True:
            content = file.read(1024)
            if not content: 
                break
            client_socket.send(content)

    print("Arquivo enviado!\n\n")


    

