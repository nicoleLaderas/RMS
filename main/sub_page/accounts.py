import os
import shutil
from tkinter import filedialog, messagebox
import mysql.connector
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage
from PIL import Image, ImageTk
import tkinter as tk
from datetime import date, datetime
from tkcalendar import DateEntry


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


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


def clear_entries_user(username_entry, password_entry, full_name_entry, sex_entry, contact_info_entry, role_combobox):
    for entry in [username_entry, password_entry, full_name_entry, sex_entry, contact_info_entry]:
        entry.delete(0, tk.END)
    role_combobox.set('')

# Add new user function
def add_user(username, password, full_name, sex, contact_info, role,user_treeview,conn):
    try:
        cursor = conn.cursor()

        # Check if the username already exists
        check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()
        confirm = messagebox.askyesno("Confirm", " Are you sure you want to add this account?")
        if not confirm:
                return

        if result[0] > 0:
            print(f"Username '{username}' already exists. Please choose a different username.")
            return  # Exit the function if the username exists

        # Insert the new user if the username is unique
        insert_query = "INSERT INTO users (username, password, full_name, sex, contact_info, role) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (username, password, full_name, sex, contact_info, role))
        
        conn.commit()
        messagebox.showinfo("Success", "User Added successfully.")
        load_users_table(user_treeview,conn)
    except Exception as e:
        print(f"An error occurred while adding the user: {e}")
        conn.rollback()
    
    finally:
        cursor.close()

# Load users into the table
def load_users_table(user_treeview, conn):
    # Clear existing entries in the treeview
    for row in user_treeview.get_children():
        user_treeview.delete(row)

    # Fetch users from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        user_treeview.insert("", "end", values=row)
    cursor.close()

# Load user data into entry fields when selecting a row
def load_user_data(event, treeview, username_entry, password_entry, full_name_entry, sex_entry, contact_info_entry, role_combobox):
    selected_item = treeview.selection()
    
    if selected_item:
        item_data = treeview.item(selected_item)['values']
        
        # Assuming the columns are in the order of: user_id, username, full_name, sex, contact_info, role
        username_entry.delete(0, tk.END)
        username_entry.insert(0, item_data[1])
        
        password_entry.delete(0, tk.END)
        # Usually passwords shouldn't be displayed, but here's an example for the sake of this scenario
        password_entry.insert(0, item_data[2]) 
        
        full_name_entry.delete(0, tk.END)
        full_name_entry.insert(0, item_data[3])
        
        sex_entry.delete(0, tk.END)
        sex_entry.insert(0, item_data[4])
        
        contact_info_entry.delete(0, tk.END)
        contact_info_entry.insert(0, item_data[5])
        
        role_combobox.set(item_data[6])




def update_user(username, password, full_name, sex, contact_info, role, user_treeview, conn):
    try:
        selected_item = user_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No user selected for update.")
            return

        user_id = user_treeview.item(selected_item[0], 'values')[0]

        # Confirmation prompt
        confirm = messagebox.askyesno("Confirm Update", "Are you sure you want to update this user?")
        if not confirm:
            return

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET username = %s, password = %s, full_name = %s, sex = %s, contact_info = %s, role = %s
            WHERE user_id = %s
        """, (username, password, full_name, sex, contact_info, role, user_id))
        conn.commit()

        messagebox.showinfo("Success", "User updated successfully.")
        load_users_table(user_treeview, conn)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        conn.rollback()


def delete_user(user_treeview, conn):
    try:
        selected_item = user_treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "No user selected for deletion.")
            return

        user_id = user_treeview.item(selected_item[0], 'values')[0]

        # Confirmation prompt
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this user?")
        if not confirm:
            return

        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        messagebox.showinfo("Success", "User deleted successfully.")
        load_users_table(user_treeview, conn)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        conn.rollback()



      
def load_accounts(frame):
    clear_frame(frame)
    conn = create_connection()
    updated_width = 500
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    frame.grid_columnconfigure(2, weight=1)
    

    # Frame for user CRUD operations
    crud_frame = ttk.LabelFrame(frame, text="User Management", width=updated_width)
    crud_frame.grid(row=0, column=1, padx=10, pady=4, sticky="ew")
    frame.grid_columnconfigure(1, weight=1)
    
    # Labels and Entry Fields
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

    # Contact Info field using Entry widget
    ttk.Label(crud_frame, text="Contact Info:").grid(row=2, column=2, sticky="w", padx=20, pady=5)
    contact_info_entry = ttk.Entry(crud_frame)
    contact_info_entry.grid(row=2, column=3, padx=5, pady=5)

    ttk.Label(crud_frame, text="Role:").grid(row=3, column=2, sticky="w", padx=20, pady=5)
    role_combobox = ttk.Combobox(crud_frame, values=["Admin", "Staff", "Guest"], state="readonly")
    role_combobox.grid(row=3, column=3, padx=5, pady=5)

    # CRUD Buttons
# CRUD Buttons
    ttk.Button(crud_frame, text="Add User", command=lambda: add_user(
        username_entry.get(), password_entry.get(), full_name_entry.get(), sex_entry.get(),
        contact_info_entry.get(), role_combobox.get(),user_treeview,conn
    )).grid(row=7, column=0, padx=10, pady=20, sticky="w")

# Update User Button
    ttk.Button(crud_frame, text="Update User", command=lambda: (
            update_user(
            username_entry.get(), password_entry.get(), full_name_entry.get(),
            sex_entry.get(), contact_info_entry.get(),  role_combobox.get(),user_treeview,conn
    )
    )).grid(row=7, column=1, padx=5, pady=10, sticky="w")

    # Delete User Button
    ttk.Button(crud_frame, text="Delete User", command=lambda: (
         delete_user(user_treeview,conn)
    )).grid(row=7, column=2, padx=5, pady=10, sticky="w")


    # Frame for user table
    right_frame = ttk.LabelFrame(frame, text="User List", width=updated_width)
    right_frame.grid(row=1, column=1, padx=10, pady=4, sticky="nsew")
    frame.grid_rowconfigure(1, weight=1)

    # Treeview for displaying users
    user_treeview = ttk.Treeview(right_frame, columns=("user_id", "username","password", "full_name", "sex", "contact_info", "role"),
     show="headings", bootstyle="primary")
    user_treeview.pack(side="left", fill="both", expand=True)
    user_treeview.heading("user_id", text="User ID")
    user_treeview.heading("username", text="Username")
    user_treeview.heading("password", text="Password")
    user_treeview.heading("full_name", text="Full Name")
    user_treeview.heading("sex", text="Sex")
    user_treeview.heading("contact_info", text="Contact Info")
    user_treeview.heading("role", text="Role")

    user_treeview.column("user_id", width=100)
    user_treeview.column("username", width=120)
    user_treeview.column("password", width=120)
    user_treeview.column("full_name", width=150)
    user_treeview.column("sex", width=120)
    user_treeview.column("contact_info", width=200)
    user_treeview.column("role", width=100)
    # Vertical scrollbar for treeview
    v_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=user_treeview.yview)
    v_scrollbar.pack(side="right", fill="y")
    user_treeview.configure(yscrollcommand=v_scrollbar.set) 

    # Bind selection event
    user_treeview.bind('<<TreeviewSelect>>', lambda event: load_user_data(
        event, user_treeview, username_entry, password_entry, full_name_entry, sex_entry, contact_info_entry, role_combobox
    ))

    # Load users into table
    load_users_table(user_treeview,conn)


