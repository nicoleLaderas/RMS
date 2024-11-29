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

active_button = None 

user_id = None
current_connection = None
def exit_page(guest_window,root):
    guest_window.destroy()  
    root.deiconify()

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2  
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_connection():
    global current_connection
    if current_connection and current_connection.is_connected():
        current_connection.close()
        print("Existing connection closed.")
    current_connection = mysql.connector.connect(
        user='root',
        password='',
        port=3306,
        host='localhost',
        database='rms_db'
    )
    print("New connection established.")
    return current_connection

def user_log(id):
    global user_id
    user_id = id  # Assign global user_id
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[3]  # Assuming this is the user name or info to return
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
        conn.close()
def back_to_calendar(frame,conn):
        conn.close()
        conn = create_connection()
        clear_frame(frame)
        open_calendar(frame, conn)
def set_active_button(new_button, main_frame, load_function):
    global active_button
    conn = create_connection()
    # Revert the style of the currently active button (if any)
    if active_button and active_button.winfo_exists():
        active_button.config(bootstyle="secondary-outline")

    # Update the new button to active style
    new_button.config(bootstyle="secondary")
    active_button = new_button  # Set the new active button

    # Load the corresponding page
    load_function(main_frame,conn)

def load_table_history(treeview, conn):
    conn = create_connection()
    global user_id  # Ensure we use the global user_id
    for row in treeview.get_children():
        treeview.delete(row)

    if conn.is_connected():
        cursor = conn.cursor()
        try:
            # Query to fetch reservation details filtered by user_id
            query = """
                SELECT r.reservation_id, r.cottage_id, r.start_date, r.end_date, r.status, c.price 
                FROM reservations r 
                JOIN cottages_halls c ON r.cottage_id = c.cottage_id 
                WHERE r.user_id = %s AND r.status IN ('Confirmed', 'Pending')

            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            print(rows)
            # Insert data into Treeview
            for row in rows:
                treeview.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading reservations: {err}")
        finally:
            cursor.close()

def load_history(frame, conn):
    # Clear the frame
    clear_frame(frame)

    # Create a main frame to contain everything
    main_frame = ttk.LabelFrame(frame, text="Transaction History Table")
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Button to load transaction history
    load_transaction_button = ttk.Button(
        main_frame, text="Request Reservation", command=lambda: back_to_calendar(frame, conn)
    )
    load_transaction_button.pack(side="top", anchor="w", padx=(10, 0), pady=(10, 5))

    # Table frame for the Treeview and Scrollbar
    table_frame = ttk.Frame(main_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview for the table
    table_treeview = ttk.Treeview(
        table_frame,
        columns=("reservation_id", "cottage_id", "start_date", "end_date", "status", "amount"),
        show="headings",
        bootstyle='primary'
    )
    table_treeview.pack(side="left", fill="both", expand=True)

    # Configure table column headings
    table_treeview.heading("reservation_id", text="Reservation ID")
    table_treeview.heading("cottage_id", text="Cottage ID")
    table_treeview.heading("start_date", text="Start Date")
    table_treeview.heading("end_date", text="End Date")
    table_treeview.heading("status", text="Status")
    table_treeview.heading("amount", text="Amount")

    # Adjust column widths
    table_treeview.column("reservation_id", width=120)
    table_treeview.column("cottage_id", width=120)
    table_treeview.column("start_date", width=120)
    table_treeview.column("end_date", width=120)
    table_treeview.column("status", width=120)
    table_treeview.column("amount", width=300)

    # Vertical scrollbar for Treeview
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table_treeview.yview)
    v_scrollbar.pack(side="right", fill="y")
    table_treeview.configure(yscrollcommand=v_scrollbar.set)

    # Load data into Treeview
    load_table_history(table_treeview, conn)


def confirm_reserve(start_date, end_date, cottage_id, cottage_name,frame):
    global user_id
    confirm = messagebox.askyesno(
        "Confirm", f"Are you sure you want to reserve the cottage '{cottage_name}'?"
    )
    if confirm:
        add_reservation(user_id, cottage_id, start_date, end_date,frame)

def add_reservation(user_id, cottage_id, start_date, end_date,frame):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Validate dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

        if start_date_obj > end_date_obj:
            messagebox.showerror("Date Error", "End date cannot be before start date.")
            return

        # Check for overlapping reservations
        overlap_query = """
            SELECT COUNT(*) FROM reservations
            WHERE cottage_id = %s AND (
                (start_date <= %s AND end_date >= %s) OR
                (start_date <= %s AND end_date >= %s) OR
                (start_date >= %s AND end_date <= %s)
            )
        """
        cursor.execute(overlap_query, (
            cottage_id, start_date, start_date,
            end_date, end_date, start_date, end_date
        ))
        overlap_count = cursor.fetchone()[0]

        if overlap_count > 0:
            messagebox.showerror("Date Conflict", "Selected date range is already reserved.")
            return

        # Insert reservation
        status = "Pending"
        special_req = "None"
        insert_query = """
            INSERT INTO reservations (user_id, cottage_id, start_date, end_date, status, special_requests)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, cottage_id, start_date, end_date, status, special_req))
        conn.commit()
        messagebox.showinfo("Success", "Reservation added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add reservation: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        conn = create_connection()
        clear_frame(frame)
        open_calendar(frame, conn)

def load_avail_cottage(frame, start_date, end_date, capacity):
     # Check for missing data
    conn = create_connection()
    if not start_date or not end_date or not capacity:
        messagebox.showwarning("Missing Data", "Please fill in all the required fields (Start Date, End Date, and Capacity).")
        return

    # Confirmation dialog
    confirm = messagebox.askyesno("Confirm", f"Search cottages from {start_date} to {end_date} with capacity {capacity}?")
    if not confirm:
        return

    # Clear existing frame content
    clear_frame(frame)

    # Add header with "Go Back" button and title
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", padx=10, pady=10)

    go_back_button = ttk.Button(header_frame, text="Go Back", command=lambda: back_to_calendar(frame, conn))
    go_back_button.pack(side="left", padx=10)

    title_label = ttk.Label(header_frame, text="Available Cottages & Halls", font=("Arial", 16, "bold"))
    title_label.pack(side="left", padx=10)

    # Scrollable canvas
    canvas = ttk.Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    cards_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=cards_frame, anchor="nw")
    canvas.config(yscrollcommand=scrollbar.set)

    try:
        cursor = conn.cursor(dictionary=True)

        # Query cottages with minimum capacity
        cursor.execute("""
            SELECT * FROM cottages_halls
            WHERE capacity >= %s
        """, (capacity,))
        cottages_halls = cursor.fetchall()

        for index, cottage in enumerate(cottages_halls):
            # Check reservation conflicts for the date range
            cursor.execute("""
                SELECT * FROM reservations
                WHERE cottage_id = %s AND status = 'Pending' AND (
                    (start_date BETWEEN %s AND %s) OR
                    (end_date BETWEEN %s AND %s) OR
                    (%s BETWEEN start_date AND end_date) OR
                    (%s BETWEEN start_date AND end_date)
                )
            """, (cottage['cottage_id'], start_date, end_date, start_date, end_date, start_date, end_date))
            if cursor.fetchone():
                continue  # Skip if reserved

            # Cottage card layout
            card_frame = ttk.Frame(cards_frame, padding=10, relief="raised", width=320, height=450)
            card_frame.grid_propagate(False)
            row, col = divmod(index, 3)
            card_frame.grid(row=row, column=col, padx=10, pady=10)

            # Cottage details
            ttk.Label(card_frame, text=f"Name: {cottage['name']}", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", columnspan=2)
            ttk.Label(card_frame, text=f"Type: {cottage['type']}").grid(row=1, column=0, sticky="w", columnspan=2)
            ttk.Label(card_frame, text=f"Capacity: {cottage['capacity']}").grid(row=2, column=0, sticky="w", columnspan=2)
            ttk.Label(card_frame, text=f"Price: ${cottage['price']:.2f}").grid(row=3, column=0, sticky="w", columnspan=2)
            ttk.Label(card_frame, text=f"Description: {cottage['description']}", wraplength=200).grid(row=4, column=0, sticky="w", columnspan=2)

            # Cottage image
            image_name = cottage.get('image_name', '')
            if image_name:
                image_path = os.path.join("images", image_name)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img.thumbnail((250, 250))  # Resize
                    img_tk = ImageTk.PhotoImage(img)
                    image_label = ttk.Label(card_frame, image=img_tk)
                    image_label.image = img_tk
                    image_label.grid(row=5, column=0, columnspan=2, pady=10)

            # Select button
            ttk.Button(
                card_frame,
                text="Select",
                command=lambda c=cottage: confirm_reserve(start_date, end_date, c['cottage_id'], c['name'],frame)
            ).grid(row=6, column=0, columnspan=2, pady=10)

        # Update canvas scroll region
        cards_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Adjust grid for responsiveness
        for i in range((len(cottages_halls) + 2) // 3):
            cards_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            cards_frame.grid_columnconfigure(j, weight=1)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load cottages: {e}")
    finally:
        conn.close()

def open_calendar(frame,conn=None):

    date_frame = ttk.LabelFrame(frame, text="Choose Date")
    date_frame.grid(row=0, column=0, padx=10, pady=4, sticky="nsew")
    id = user_id
    # Allow the date_frame to expand and fill the space
 
    frame.grid_columnconfigure(0, weight=1)  # Allow the first column to expand

    ttk.Label(date_frame, text="Start Date:").grid(row=2, column=4, sticky="w", padx=20, pady=5)
    start_date_entry = ttk.DateEntry(date_frame, width=15, dateformat='%Y-%m-%d')
    start_date_entry.grid(row=2, column=5, padx=5, pady=5)

    ttk.Label(date_frame, text="End Date:").grid(row=2, column=6, sticky="w", padx=20, pady=5)
    end_date_entry = ttk.DateEntry(date_frame, width=15, dateformat='%Y-%m-%d')
    end_date_entry.grid(row=2, column=7, padx=5, pady=20)

    ttk.Label(date_frame, text="Capacity").grid(row=2, column=0, pady=5, padx=5, sticky="e")

    capacity_entry = ttk.Entry(date_frame)
    capacity_entry.grid(row=2, column=1, pady=5, padx=30, sticky="w")

    req = ttk.Button(date_frame, bootstyle="primary", text="Add Request", 
    command=lambda: load_avail_cottage(frame, start_date_entry.entry.get(), end_date_entry.entry.get(), capacity_entry.get() ))
    req.grid(row=2, column=8, padx=20, pady=20)
    




def open_guest (id,root):
    conn = create_connection()

    root.withdraw()
    guest_window = ttk.Toplevel()
    guest_window.title("Guest")
    user = user_log(id)

    center_window(guest_window, 1350, 800)

    guest_window.grid_rowconfigure(1, weight=1) 
    guest_window.grid_columnconfigure(1, weight=1) 

    left_frame = ttk.Frame(guest_window, bootstyle="primary", width=300)
    left_frame.grid(row=0, column=0, rowspan=2, sticky="ns")
    left_frame.pack_propagate(False) 

    main_frame = ttk.Frame(guest_window, bootstyle="light")
    main_frame.grid(row=1, column=1, sticky="nsew")

    top_frame = ttk.Frame(guest_window, bootstyle="secondary", height=60)
    top_frame.grid(row=0, column=1, sticky="ew")
    top_frame.pack_propagate(False)
    ttk.Label(top_frame, text=f"Hi Guest! : {user}", bootstyle="inverse-secondary", font=("Arial", 18)).pack(pady=10)
    
    title_page = ttk.Label(left_frame, bootstyle="inverse-primary", text="Resort Management System", font=("Roboto", 15, "bold"), wraplength=260)
    title_page.pack(pady=(0,30), fill='x')

    # Cottage Button
    page_cottage = ttk.Button(
        left_frame,
        text="Request",
        bootstyle="secondary-outline",
        padding="20",
        command=lambda: set_active_button(page_cottage, main_frame, back_to_calendar)
    )# 
    page_cottage.pack(fill="x", pady=2)

    # History
    page_accounts = ttk.Button(
        left_frame,
        text="Transaction history",
        bootstyle="secondary-outline",
        padding="20",
        command=lambda: set_active_button(page_accounts, main_frame, load_history)
        
    )
    page_accounts.pack(fill="x", pady=2)

    exit_btn = ttk.Button(left_frame,bootstyle="danger",text="Exit",command=lambda: exit_page(guest_window,root) )
    exit_btn.pack(pady=30)

   
    open_calendar(main_frame,conn)

  