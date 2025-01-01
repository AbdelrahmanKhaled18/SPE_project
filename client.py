import os
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
import socket
import cv2
import numpy as np
import json
import base64
from communication_helper import *

client_socket = None
processed_images = []


def connect_to_server():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to the server")
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        showinfo("Error", "Failed to connect to the server.")


def send_json(client_socket: socket.socket, images, selected_option):
    encoded_images = []
    for img in images:
       
        _, img_encoded = cv2.imencode(".jpg", img)
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")
        encoded_images.append(img_base64)

    payload = {
        "selected_option": selected_option,
        "num_images": len(images),
        "images": encoded_images,
    }


    json_data = json.dumps(payload).encode("utf-8")
    client_socket.sendall(len(json_data).to_bytes(8, byteorder="big"))
    client_socket.sendall(json_data)


def receive_json(client_socket: socket.socket):
    
    data_size = int.from_bytes(client_socket.recv(8), byteorder="big")
    raw_data = recvall(client_socket, data_size).decode("utf-8")
    json_data = json.loads(raw_data)

    images = []
    for img_base64 in json_data.get("processed_images", []):
        img_data = base64.b64decode(img_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        images.append(image)
    return images


def send_raw_bytes(client_socket: socket.socket, images, selected_option):
    client_socket.sendall(selected_option.encode())

   
    client_socket.sendall(len(images).to_bytes(8, byteorder="big"))
    for img in images:
       
        client_socket.sendall(img.shape[0].to_bytes(8, byteorder="big"))
    
        client_socket.sendall(img.shape[1].to_bytes(8, byteorder="big"))

        client_socket.sendall(img.astype(np.ubyte).tobytes())


def receive_raw_bytes(client_socket: socket.socket, image_sizes):
    images = []  
    for image_size in image_sizes:
        rows, cols = image_size
        bytes_no = rows * cols * 3
        raw_image = recvall(client_socket, bytes_no)
        images.append(
            np.frombuffer(raw_image, dtype=np.ubyte)
            .reshape(rows, cols, 3)
            .astype(np.uint8)
        )
    return images


def upload_file(file_paths, selected_option):
    file_paths = file_paths.split("\n")

    if file_paths and any(file_paths):
        try:
            
            images = [cv2.imread(p) for p in file_paths]

            if PROTOCOL == Protocol.JSON:
                send_json(client_socket, images, selected_option)
            if PROTOCOL == Protocol.BYTES:
                send_raw_bytes(client_socket, images, selected_option)
            print("Sent all images to the server.")

            global processed_images
            if PROTOCOL == Protocol.JSON:
                processed_images = receive_json(client_socket)
            if PROTOCOL == Protocol.BYTES:
                image_sizes = [img.shape[0:2] for img in images]
                processed_images = receive_raw_bytes(client_socket, image_sizes)
            print("Received processed images from server.")

        except FileNotFoundError as e:
            showinfo("Error", str(e))
        except OSError as e:
            print(f"Connection error: {e}")
            reconnect_to_server()
        except BrokenPipeError as e:
            print(f"Broken pipe error: {e}")
            reconnect_to_server()
    else:
        showinfo("Error", "Please select one or more files to upload.")


def download_images(images):
    # Download the processed images.

    if not images:
        showinfo("Error", "No images to download.")
        return

    valid_extensions = [".jpg", ".jpeg", ".png"]
    for i, img in enumerate(images):
        file_extension = ".jpg"  # Default file extension
        save_path = filedialog.asksaveasfilename(
            defaultextension=file_extension,
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*"),
            ],
        )

        # Ensure the save_path has a valid extension
        if not any(save_path.lower().endswith(ext) for ext in valid_extensions):
            # Default to .jpg if no valid extension is found
            save_path += file_extension

        try:
            cv2.imwrite(save_path, img)
            showinfo("Success", f"Image {i + 1} has been downloaded.")
        except cv2.error as e:
            showinfo("Error", f"Failed to save image {i + 1}: {e}")


def reconnect_to_server():
    print("Trying to reconnect...")
    global client_socket

    try:
        # Close the socket if it's still open
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print("Closed existing connection")
    except Exception as e:
        print(f"Error closing existing connection: {e}")

    try:
        # Reconnect to the server
        connect_to_server()
    except Exception as e:
        print(f"Error reconnecting to server: {e}")


if __name__ == "__main__":
    img_names = [
        "Screenshot_453.png",
        "Screenshot_454.png",
        "Screenshot_455.png",
        "Screenshot_456.png",
        "Screenshot_457.png",
        "Screenshot_459.png",
    ]

    dir = os.path.dirname(__file__)
    img_paths_list = [os.path.join(dir, "static", img_name) for img_name in img_names]
    img_paths_string = "\n".join(img_paths_list)
    selected_option = "enhance"
    connect_to_server()
    upload_file(img_paths_string, selected_option)
