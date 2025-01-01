# Application Overview

This project is a client-server application designed to perform image processing tasks. It uses a graphical user interface (GUI) for user interaction and supports multiple image processing operations such as edge detection, color inversion, Gaussian blur, and more. The application includes profiling capabilities to monitor performance.

## Features

- **Image Upload and Processing**: Users can upload images via the GUI, select processing options, and download processed images.
- **Multithreaded Server**: The server processes images using multithreading for efficient performance.
- **Multiple Processing Options**: Supports a variety of image processing techniques, including edge detection, color inversion, and histogram equalization.
- **Profiling and Testing**: Includes a profiling program to monitor server performance while handling concurrent client connections.

## Files and Components

### 1. `client.py`
- Handles the client-side operations, including:
  - Connecting to the server.
  - Sending and receiving images in JSON or raw byte formats.
  - Uploading and downloading files via the GUI.
- Dependencies:
  - OpenCV for image manipulation.
  - `communication_helper.py` for protocol and communication utilities.

### 2. `communication_helper.py`
- Contains shared utilities for both the client and server, including:
  - Protocol enumeration (JSON or raw bytes).
  - Constants for server host and port configuration.
  - A helper function (`recvall`) to handle socket communication.

### 3. `GUI.py`
- Implements the graphical user interface for the application using `tkinter`.
- Key Features:
  - File selection and upload options.
  - Processing option menu for users to choose desired image transformations.
  - Download functionality to save processed images.
- Depends on `client.py` for backend communication.

### 4. `server.py`
- The server-side script responsible for:
  - Accepting client connections and processing image data.
  - Implementing multithreaded image processing.
  - Supporting a variety of image processing options.
  - Logging activities for debugging and performance analysis.
- Uses a `ThreadPool` for processing image chunks concurrently.

### 5. `profiling_program.py`
- Profiles the performance of the server under concurrent client connections.
- Key Features:
  - Launches the server with `cProfile`.
  - Simulates 20 parallel clients uploading and processing images.
  - Saves profiling data to a `.prof` file and a detailed `.txt` report.
  - Optionally visualizes profiling results using `snakeviz`.

## Setup and Installation

### Prerequisites
- Python 3.8 or later.
- Required libraries: `tkinter`, `opencv-python`, `numpy`, `snakeviz`.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install opencv-python numpy
   ```
3.  Install Snakeviz for profiling visualization:
   ```bash
   pip install snakeviz
   ```

## Usage

### Profiling the Application
1. Run the profiling program:
   ```bash
   python profiling_program.py
   ```
2. View the profiling results in `profiling_results.txt` and visualize them using Snakeviz.

## Project Structure
```
project-folder/
├── client.py                  # Client-side logic
├── communication_helper.py    # Shared communication utilities
├── GUI.py                     # Graphical user interface
├── server.py                  # Server-side logic
├── profiling_program.py       # Profiling and performance testing
```

