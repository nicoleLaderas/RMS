
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import mysql.connector
from main.sub_page.cottage import load_cottage
from main.sub_page.reservation import load_reservation
from main.sub_page.dashboard import load_dashboard
from main.sub_page.confirm import load_confirmation
from main.sub_page.accounts import load_accounts


# Initialize the ttkbootstrap style




def create_connection():
    connection = mysql.connector.connect(
        user='root',
        password='', 
        port=3306,
        host='localhost',
        database='rms_db'  
    )
    return connection


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 
    window.geometry(f"{width}x{height}+{x}+{y}")

def exit_page(admin_window,root):
    admin_window.destroy()  
    root.deiconify()

def user_log(id):
    con = create_connection()
    cursor = con.cursor()
    user_id = id 

    try:
        query = "select * from users where user_id  = %s"
        cursor.execute(query,(user_id,))
        result = cursor.fetchone()
        if result:
            return result[3]
        
        
    except Exception as e:
        print(f"Error executing the query: {e}")
    finally:
        cursor.close()
        con.close()
active_button = None 
def set_active_button(new_button, main_frame, load_function):
    global active_button

    # Revert the style of the currently active button (if any)
    if active_button and active_button.winfo_exists():
        active_button.config(bootstyle="secondary-outline")

    # Update the new button to active style
    new_button.config(bootstyle="secondary")
    active_button = new_button  # Set the new active button

    # Load the corresponding page
    load_function(main_frame)

def open_admin (id,root):
    root.withdraw()
    admin_window = ttk.Toplevel()
    admin_window.title("Admin")
   
    center_window(admin_window, 1350, 800)

    
    admin_window.grid_rowconfigure(1, weight=1) 
    admin_window.grid_columnconfigure(1, weight=1) 

    user = user_log(id)
    
    left_frame = ttk.Frame(admin_window, bootstyle="primary", width=300)
    left_frame.grid(row=0, column=0, rowspan=2, sticky="ns")
    left_frame.pack_propagate(False) 

    main_frame = ttk.Frame(admin_window, bootstyle="light")
    main_frame.grid(row=1, column=1, sticky="nsew")

    top_frame = ttk.Frame(admin_window, bootstyle="secondary", height=60)
    top_frame.grid(row=0, column=1, sticky="ew")
    top_frame.pack_propagate(False)
    ttk.Label(top_frame, text=f"Hi Admin! : {user}", bootstyle="inverse-secondary", font=("Arial", 18)).pack(pady=10)
    
    title_page = ttk.Label(left_frame, bootstyle="inverse-primary", text="Resort Management System", font=("Roboto", 15, "bold"), wraplength=260)
    title_page.pack(pady=(0,30), fill='x')

   # Button Definitions
 # Button Definitions
    page_dashboard = ttk.Button(
        left_frame,
        text="Dashboard",
        bootstyle="secondary-outline", 
        padding="20",
        command=lambda: set_active_button(page_dashboard, main_frame, load_dashboard)
    )
    page_dashboard.pack(fill="x", pady=2)  

    page_cottage = ttk.Button(
        left_frame,
        text="Cottage",
        bootstyle="secondary-outline",  # Changed to 'secondary-outline'
        padding="20",
        command=lambda: set_active_button(page_cottage, main_frame, load_cottage)
    )
    page_cottage.pack(fill="x", pady=2)  

    page_reservation = ttk.Button(
        left_frame,
        text="Reservation",
        bootstyle="secondary-outline",  # Changed to 'secondary-outline'
        padding="20",
        command=lambda: set_active_button(page_reservation, main_frame, load_reservation)
    )
    page_reservation.pack(fill="x",pady=2) 

    page_confirmation = ttk.Button(
        left_frame,
        text="Confirmation",
        bootstyle="secondary-outline",  # Already 'secondary-outline'
        padding="20",
        command=lambda: set_active_button(page_confirmation, main_frame, load_confirmation)
    )
    page_confirmation.pack(fill="x", pady=2)  

    page_accounts = ttk.Button(
        left_frame,
        text="Accounts",
        bootstyle="secondary-outline",  #
        padding="20",
        command=lambda: set_active_button(page_accounts, main_frame, load_accounts)
    )
    page_accounts.pack(fill="x", pady=2) 

    
    load_dashboard(main_frame) 
    exit_btn = ttk.Button(left_frame,bootstyle="danger",text="Exit",command=lambda: exit_page(admin_window,root) )
    exit_btn.pack(pady=30)

  



