from client import *


def browse_file(file_entry):
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        file_entry.config(state="normal")
        file_entry.delete(0, "end")
        file_entry.insert(0, "\n".join(file_paths))
        file_entry.config(state="readonly")


def create_form_elements(root):
    # Create form elements such as labels, buttons, and entry fields.

    file_label = Label(root, text="File:", background="#0078D4", font="bold")
    file_entry = Entry(root, state="readonly")
    file_button = Button(
        root,
        text="Browse",
        command=lambda: browse_file(file_entry),
        background="white",
        highlightbackground="white",
        highlightcolor="white",
    )
    upload_button = Button(
        root,
        text="Upload File",
        command=lambda: upload_file(file_entry.get().strip(), selected_option.get()),
        background="white",
        highlightbackground="white",
        highlightcolor="white",
    )

    download_button = Button(
        root,
        text="Download Image",
        command=lambda: download_images(processed_images),
        background="white",
        highlightbackground="white",
        highlightcolor="white",
    )

    options = [
        "edge_detection",
        "color_inversion",
        "erosion",
        "dilation",
        "adaptive_threshold",
        "histogram_equalization",
        "sharpen",
        "gaussian_blur",
        "enhance",
    ]
    selected_option = StringVar()
    selected_option.set(options[0])
    option_menu = OptionMenu(root, selected_option, *options)
    file_label.place(x=110, y=144)
    file_entry.place(x=160, y=150)
    file_button.place(x=287, y=147)
    upload_button.place(x=212, y=200)
    download_button.place(x=198, y=240)
    option_menu.place(x=185, y=280)


connect_to_server()
root = Tk()
root.geometry("450x400")  # starting window size
root.configure(bg="#0078D4")  # GUI background color
create_form_elements(root)
root.mainloop()
