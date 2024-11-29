from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import PhotoImage
import os
from db.auth import check_user
from PIL import Image, ImageTk
import mysql.connector


current_connection = None

def create_connection():
    global current_connection
    # Check if a connection already exists and close it
    if current_connection and current_connection.is_connected():
        current_connection.close()
        print("Existing connection closed.")
    
    # Create a new connection
    current_connection = mysql.connector.connect(
        user='root',
        password='',
        port=3306,
        host='localhost',
        database='rms_db'
    )
    print("New connection established.")
    return current_connection

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 
    window.geometry(f"{width}x{height}+{x}+{y}")

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def go_to_registration(root,conn):
    clear_frame(root)
    load_register_guest(root,conn)

def back_to_login(root):
    clear_frame(root)
    open_login(root)

def add_user(username, password, full_name, sex, contact_info, conn, root):
 
    try:
        cursor = conn.cursor()

        # Check if the username already exists
        check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()
        confirm = messagebox.askyesno("Confirm", "Confirm Register Account?")
        if not confirm:
            return

        if result[0] > 0:
            messagebox.showwarning("Warning", f"Username '{username}' already exists. Please choose a different username.")
            return  # Exit the function if the username exists

        # Insert the new user if the username is unique
        role = "Guest"
        insert_query = "INSERT INTO users (username, password, full_name, sex, contact_info, role) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (username, password, full_name, sex, contact_info, role))
        
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully.")
        back_to_login(root)  # Navigate back to login screen
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
def load_register_guest(root, conn):
    clear_frame(root)  # Clear the frame before adding new widgets


    # Create a new frame within the parent frame
    crud_frame = ttk.LabelFrame(root, text="User Management")
    crud_frame.grid(padx=10, pady=4, sticky="nsew")  # Use grid instead of pack


    ttk.Label(crud_frame, text="Username:").grid(row=1, column=0, sticky="w", padx=20, pady=5)
    username_entry = ttk.Entry(crud_frame)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(crud_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=20, pady=5)
    password_entry = ttk.Entry(crud_frame, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(crud_frame, text="Full Name:").grid(row=3, column=0, sticky="w", padx=20, pady=5)
    full_name_entry = ttk.Entry(crud_frame)
    full_name_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(crud_frame, text="Sex:").grid(row=1, column=2, sticky="w", padx=20, pady=5)
    sex_entry = ttk.Entry(crud_frame)
    sex_entry.grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(crud_frame, text="Contact Info:").grid(row=2, column=2, sticky="w", padx=20, pady=5)
    contact_info_entry = ttk.Entry(crud_frame)
    contact_info_entry.grid(row=2, column=3, padx=5, pady=5)

    ttk.Button(crud_frame, text="Add User", command=lambda: add_user(
        username_entry.get(), password_entry.get(), full_name_entry.get(), sex_entry.get(),
        contact_info_entry.get(), conn,root
    )).grid(row=7, column=0, padx=10, pady=20, sticky="w")

    back = ttk.Button(crud_frame, text="Back to Login", command=lambda: back_to_login(root))
    back.grid(row=7, column=1, padx=10, pady=20, sticky="w")

def open_login(root):
    # Clear the root frame before rebuilding the login UI
    clear_frame(root)

    root.title("Login - RMS")
    center_window(root, 1200, 600)
    root.resizable(False, False)

    conn = create_connection()

    root.grid_columnconfigure(0, weight=1) 
    root.grid_columnconfigure(1, minsize=400)  
    root.resizable(False, False)

    # Image for login
    script_dir = os.path.dirname(__file__)
    print(f"Script{script_dir}")
    image_path = os.path.join(script_dir, "images", "login-beach.png")
    img = Image.open(image_path)
    max_width = 1000
    img.thumbnail((max_width, max_width))
    login_image = ImageTk.PhotoImage(img)

    # Frame 1: For the image
    frame1 = ttk.Frame(root)
    frame1.grid(row=0, column=0, sticky="nsew", padx=0, pady=0) 
    
    label = ttk.Label(frame1, image=login_image)
    label.image = login_image  # Keep a reference to avoid garbage collection
    label.pack(fill="both", expand=True)

    frame2 = ttk.Frame(root, bootstyle='primary')
    frame2.grid(row=0, column=1, sticky="nsew", padx=0, pady=0) 

    title = ttk.Label(frame2, bootstyle='inverse-primary', text="Resort Management System", font=("Roboto", 18, "bold"), wraplength=360)
    title.pack(pady=(40, 10))

    username_label = ttk.Label(frame2, bootstyle="inverse-primary", text="Username:", anchor="w", width=20)
    username_label.pack(pady=(20, 5), padx=100, fill='x') 

    username_entry = ttk.Entry(frame2)
    username_entry.pack(fill="x", padx=100) 

    password_label = ttk.Label(frame2, bootstyle="inverse-primary", text="Password:", anchor="w", width=20) 
    password_label.pack(pady=(20, 5), padx=100, fill='x') 

    password_entry = ttk.Entry(frame2, show="*")
    password_entry.pack(fill="x", padx=100)  



    login_button = ttk.Button(frame2, bootstyle="info-outline", text="Login", command=lambda: check_user(conn, username_entry.get(), password_entry.get(), root))
    login_button.pack(pady=20)

    register_btn = ttk.Button(frame2, bootstyle="info-outline", text="Guest Register", command=lambda: go_to_registration(root, conn))
    register_btn.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    root = ttk.Window(themename="pulse")  # Create the root window
    open_login(root)  # Pass the root window to the function
    root.mainloop()

