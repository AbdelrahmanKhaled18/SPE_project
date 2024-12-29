import socket
import cv2
import numpy as np
import logging
import time
import json
import base64

SERVER_HOST = "localhost"
SERVER_PORT = 1234

# Initialize logging
initTime = time.time()
logging.basicConfig(
    filename="log.txt",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


def log(step: str):
    logging.info(f"{step}: {time.time() - initTime:.4f}s")


def process_image(image, selected_option):
    try:
        log(f"Processing image with option {selected_option}")

        if selected_option == "edge_detection":
            processed_image = cv2.Canny(image, 100, 200)
        elif selected_option == "color_inversion":
            processed_image = cv2.bitwise_not(image)
        elif selected_option == "gaussian_blur":
            processed_image = cv2.GaussianBlur(image, (5, 5), 0)
        elif selected_option == "sharpen":
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            processed_image = cv2.filter2D(image, -1, kernel)
        elif selected_option == "histogram_equalization":
            if len(image.shape) == 2:
                processed_image = cv2.equalizeHist(image)
            else:
                img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
                img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
                processed_image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        elif selected_option == "adaptive_threshold":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            processed_image = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        elif selected_option == "dilation":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
            processed_image = cv2.dilate(image, kernel)
        elif selected_option == "erosion":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
            processed_image = cv2.erode(image, kernel)
        elif selected_option == "enhance":
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
            kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]])
            processed_image = cv2.filter2D(enhanced_image, -1, kernel)
        else:
            log("Invalid processing option. Returning original image.")
            processed_image = image

        log("Processing completed")
        return processed_image
    except Exception as e:
        log(f"Error processing image: {e}")
        return image


def receive_data(client_socket):
    payload_size = int.from_bytes(client_socket.recv(8), byteorder="big")
    log(f"Expecting JSON payload of size {payload_size} bytes")

    payload_data = client_socket.recv(payload_size).decode("utf-8")
    payload = json.loads(payload_data)
    log("Received JSON payload")

    selected_option = payload["selected_option"]
    images_base64 = payload["images"]

    decoded_images = []
    for img_base64 in images_base64:
        img_data = base64.b64decode(img_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            log("Failed to decode the received image. Skipping processing.")
            continue

        decoded_images.append(img)
        log(f"Image decoded. Dimensions: {img.shape}")
    return (selected_option, decoded_images)


def send_data(client_socket, images):
    processed_images_base64 = []
    for image in images:
        _, img_encoded = cv2.imencode(".jpg", image)
        processed_base64 = base64.b64encode(img_encoded).decode("utf-8")
        processed_images_base64.append(processed_base64)

    response = {"processed_images": processed_images_base64}
    response_data = json.dumps(response).encode("utf-8")
    client_socket.sendall(len(response_data).to_bytes(8, byteorder="big"))
    client_socket.sendall(response_data)


def handle_client(client_socket):
    try:
        selected_option, images = receive_data(client_socket)

        processed_images = []
        for img_index, img in enumerate(images):
            log(f"Processing image {img_index + 1}/{len(images)}")
            start_time = time.time()
            processed_img = process_image(img, selected_option)
            processing_time = time.time() - start_time
            log(f"Image processed in {processing_time:.4f}s")
            processed_images.append(processed_img)

        send_data(client_socket, processed_images)
        log("Processed images sent back to client")

    except Exception as e:
        log(f"Error handling client: {e}")
    finally:
        client_socket.close()
        log("Client connection closed")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    log(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            log(f"Connection from {client_address}")
            handle_client(client_socket)

    finally:
        server_socket.close()
        log("Server socket closed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log(f"Unhandled exception in main: {e}")
    finally:
        log("Shutting down the server...")
