import socket
import cv2
import numpy as np

PORT = 14000
IMG_PATH = "./img_recv.jpg"


def receive_and_rotate_image(connection):
    chunks = []
    while True:
        content = connection.recv(1024)
        if not content:
            break
        chunks.append(content)

    print("Arquivo recebido!")

    image_data = b''.join(chunks)
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    print("Rotacionando...\n")
    img_180 = cv2.rotate(img, cv2.ROTATE_180)

    cv2.imwrite(IMG_PATH, img_180)
    print("Imagem rotacionada e salva!")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(("", PORT))
    server_socket.listen(0)

    connection, address = server_socket.accept()
    print(f"{address[0]} conectou\n")

    receive_and_rotate_image(connection)



