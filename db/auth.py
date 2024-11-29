from tkinter import messagebox
import mysql.connector
from main.admin import open_admin
from main.guest import open_guest
from main.staff import open_staff




def create_connection():
    connection = mysql.connector.connect(
        user='root',
        password='', 
        port=3306,
        host='localhost',
        database='rms_db'  
    )
    return connection


def check_user(conn, username, password,root=None):
    try:
        # Use the connection to create a cursor
        cursor = conn.cursor()
        
        # Execute the query
        query = "SELECT role,user_id FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            print(result)
            go_page(result[0],result[1],root)
            
        else:
            print("error")
            messagebox.showerror("Error", "Wrong credentials")
    except Exception as e:
        print(f"Error executing the query: {e}")

def go_page(role,id,root):
    print(role)
    try:
        if role == "Admin":
            open_admin(id,root)
        elif role == "Staff":
            open_staff(id,root)
        elif role == "Guest":
            open_guest(id,root)
        else:
             messagebox.showerror("Failed", "Invalid Info")
    finally:
       
       print("success")


