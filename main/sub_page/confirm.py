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

# For adding and deleting value on the entries
def clear_entry(event, entry, default_text):

    if entry.get() == default_text:
        entry.delete(0, tk.END)

def set_default_text(entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)


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

def load_table_confirmation(treeview, conn):
    # Clear existing rows
    for row in treeview.get_children():
        treeview.delete(row)

    if conn.is_connected():
        cursor = conn.cursor()
        try:
            # Query to fetch reservation details along with cottage price
            query = """
                SELECT r.reservation_id, r.user_id, r.cottage_id, r.start_date, r.end_date, r.status, c.price 
                FROM reservations r 
                JOIN cottages_halls c ON r.cottage_id = c.cottage_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print(rows)
            # Insert data into Treeview
            for row in rows:
                treeview.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading reservations: {err}")
        finally:
            cursor.close()

def confirm_reservation(table_treeview, conn):
    # Get selected item
    selected_item = table_treeview.selection()

    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a reservation to confirm.")
        return

    # Get reservation details from the selected item
    selected_data = table_treeview.item(selected_item)['values']
    reservation_id = selected_data[0]
    
    try:
        # Convert the amount to a float for proper formatting
        amount = float(selected_data[6])  # Price column from the Treeview
    except (ValueError, IndexError):
        messagebox.showerror("Error", "Invalid amount value for the selected reservation.")
        return

    # Confirm the user's choice
    confirm = messagebox.askyesno("Confirm Reservation", f"Are you sure you want to confirm this reservation?\nAmount: {amount:.2f}")
    if not confirm:
        return

    try:
        cursor = conn.cursor()

        # Update reservation status to 'Confirmed'
        update_query = "UPDATE reservations SET status = 'Confirmed' WHERE reservation_id = %s"
        cursor.execute(update_query, (reservation_id,))

        # Insert data into the transactions table
        insert_query = """
            INSERT INTO transactions (reservation_id, amount, status)
            VALUES (%s, %s, 'Confirmed')
        """
        cursor.execute(insert_query, (reservation_id, amount))
        conn.commit()

        # Reload the table to reflect the change
        load_table_confirmation(table_treeview, conn)
        
        messagebox.showinfo("Success", "Reservation confirmed and transaction recorded successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"An error occurred: {err}")
    finally:
        if conn.is_connected():
            cursor.close()

def search_reservations(search_entry, table_treeview,conn):
        # Get the search input from the entry
        search_term = search_entry.get().strip()

        # Return if the search term is empty or the default text
        if not search_term or search_term == "Enter the name of Cottage | Guest | Reservation | ID":
            messagebox.showwarning("Invalid Search", "Please enter a valid search term.")
            return

        try:
            cursor = conn.cursor()

            # Prepare search query, use LIKE for partial matching
            search_query = """
            SELECT 
                r.reservation_id, 
                r.user_id, 
                r.cottage_id, 
                r.start_date, 
                r.end_date, 
                r.status, 
                r.special_requests, 
                u.full_name, 
                c.name 
            FROM 
                reservations r
            JOIN 
                users u ON r.user_id = u.user_id
            JOIN 
                cottages_halls c ON r.cottage_id = c.cottage_id
            WHERE 
                r.reservation_id = %s OR
                u.full_name LIKE %s OR
                c.name LIKE %s
            """

            # Use search term as a parameter for the query
            cursor.execute(search_query, (search_term, f"%{search_term}%", f"%{search_term}%"))
            results = cursor.fetchall()

            # Clear the current table contents
            for row in table_treeview.get_children():
                table_treeview.delete(row)

            # Insert new search results into the table
            for row in results:
                # Extract only the needed columns for display
                table_treeview.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"An error occurred: {err}")
        finally:
                cursor.close()

def load_table_transaction(treeview, conn):
    # Clear existing rows
    for row in treeview.get_children():
        treeview.delete(row)

    if conn.is_connected():
        cursor = conn.cursor()
        try:
            # Query to fetch reservation details along with cottage price
            query = """
                SELECT r.reservation_id, r.user_id, r.cottage_id, r.start_date, r.end_date, r.status, c.price 
                FROM reservations r 
                JOIN cottages_halls c ON r.cottage_id = c.cottage_id Where status = 'Confirmed'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print(rows)
            # Insert data into Treeview
            for row in rows:
                treeview.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading reservations: {err}")
        finally:
            cursor.close()
def load_transaction(frame, conn):
    # Clear the frame
    clear_frame(frame)

    # Create a main frame to contain everything
    main_frame = ttk.LabelFrame(frame, text="Transaction History Table")
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Button to load transaction history
    load_transaction_button = ttk.Button(
        main_frame, text="Back to Confirmation", command=lambda: load_confirmation(frame)
    )
    load_transaction_button.pack(side="top", anchor="w", padx=(10, 0), pady=(10, 5))

    # Table frame for the Treeview and Scrollbar
    table_frame = ttk.Frame(main_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview for the table
    table_treeview = ttk.Treeview(
        table_frame,
        columns=("reservation_id", "user_id", "cottage_id", "start_date", "end_date", "status", "amount"),
        show="headings",
        bootstyle='primary'
    )
    table_treeview.pack(side="left", fill="both", expand=True)

    # Configure table column headings
    table_treeview.heading("reservation_id", text="Reservation ID")
    table_treeview.heading("user_id", text="User ID")
    table_treeview.heading("cottage_id", text="Cottage ID")
    table_treeview.heading("start_date", text="Start Date")
    table_treeview.heading("end_date", text="End Date")
    table_treeview.heading("status", text="Status")
    table_treeview.heading("amount", text="Amount")

    # Adjust column widths
    table_treeview.column("reservation_id", width=120)
    table_treeview.column("user_id", width=80)
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
    load_table_transaction(table_treeview, conn)


def load_confirmation(frame):
    conn = create_connection()
    # Clear the existing frame contents
    clear_frame(frame)

    # Create a main frame to contain everything, with grid layout
    main_frame = ttk.LabelFrame(frame, text="Reservation Table")
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Create a sub-frame for the buttons and search entry
    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill="x", padx=10, pady=(10, 0))

    # Confirm button on the left side
    confirm_button = ttk.Button(search_frame, text="Confirm Reservation", command=lambda: confirm_reservation(table_treeview,conn))
    confirm_button.pack(side="left", padx=(0, 5))
    
    reset_btn = ttk.Button(search_frame, text="Reload Table", command=lambda:  load_table_confirmation(table_treeview,conn))
    reset_btn.pack(side="left", padx=(0, 5))
    load_transcation = ttk.Button(search_frame, text="Transaction History",command=lambda: load_transaction(frame,conn))
    load_transcation.pack(side="left", padx=(0, 5))


    # Search entry with resized width
    search_entry = ttk.Entry(search_frame, width=40)
    search_entry.pack(side="right", padx=5, fill="x", expand=True)
    default = "Enter the name of Cottage | Guest | Reservation | ID"
    search_entry.insert(0, default)

    search_entry.bind("<FocusIn>", lambda event: clear_entry(event, search_entry, default))
    search_entry.bind("<FocusOut>", lambda event: set_default_text(search_entry, default))

    # Search button to the right of the entry
    search_button = ttk.Button(search_frame, text="Search", command=lambda: search_reservations(search_entry, table_treeview,conn))
    search_button.pack(side="right", padx=(10, 5))

    # Frame for the table and scrollbar
    table_frame = ttk.Frame(main_frame)  # Make sure this is created inside the function
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Table (Treeview) widget
    table_treeview = ttk.Treeview(
        table_frame,
        columns=("reservation_id", "user_id", "cottage_id", "start_date", "end_date", "status", "amount"),
        show="headings",
        bootstyle='primary'
    )
    table_treeview.pack(side="left", fill="both", expand=True)

    # Table column headings
    table_treeview.heading("reservation_id", text="Reservation ID")
    table_treeview.heading("user_id", text="User ID")
    table_treeview.heading("cottage_id", text="Cottage ID")
    table_treeview.heading("start_date", text="Start Date")
    table_treeview.heading("end_date", text="End Date")
    table_treeview.heading("status", text="Status")
    table_treeview.heading("amount", text="Amount")

    # Adjust column widths to reduce spacing
    table_treeview.column("reservation_id", width=120)
    table_treeview.column("user_id", width=80)
    table_treeview.column("cottage_id", width=120)
    table_treeview.column("start_date", width=120)
    table_treeview.column("end_date", width=120)
    table_treeview.column("status", width=120)
    table_treeview.column("amount", width=300)

    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table_treeview.yview)
    v_scrollbar.pack(side="right", fill="y")
    # Vertical scrollbar for Treeview
    table_treeview.configure(yscrollcommand=v_scrollbar.set)

    # Load reservation data into the table
    load_table_confirmation(table_treeview,conn)

