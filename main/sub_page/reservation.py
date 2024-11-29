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

def load_avail_cottage_cards(frame,conn):
    clear_frame(frame)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", padx=10, pady=10)


    go_back_button = ttk.Button(header_frame, text="Go Back", command=lambda: load_reservation(frame))
    go_back_button.pack(side="left", padx=10)


    title_label = ttk.Label(header_frame, text="Available Cottages & Halls", font=("Arial", 16, "bold"))
    title_label.pack(side="left", padx=10)

   
    canvas = ttk.Canvas(frame)
    canvas.pack(side="left", fill="both", expand=True)


    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview, bootstyle="primary")
    scrollbar.pack(side="right", fill="y")

 
    cards_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=cards_frame, anchor="nw")

    
    canvas.config(yscrollcommand=scrollbar.set)

    # Connect to the database to retrieve cottages/halls data
    try:

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cottages_halls")
        cottages_halls = cursor.fetchall()
      
        cottage_id = cottages_halls[0]
        print(cottage_id)

        for index, cottage in enumerate(cottages_halls):
            # Create a frame for each cottage/hall card with fixed size
            card_frame = ttk.Frame(cards_frame, bootstyle="light", padding=10, relief="raised", width=320, height=450)
            card_frame.grid_propagate(False)  # Prevent resizing based on content
            
            # Use grid to organize cards
            row = index // 3  # Adjust 3 to the number of cards per row you want
            col = index % 3
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Cottage/Hall details
            name_label = ttk.Label(card_frame, text=f"Name: {cottage['name']}", font=("Arial", 12, "bold"))
            name_label.grid(row=1, column=0, sticky="w", columnspan=2)

            type_label = ttk.Label(card_frame, text=f"Type: {cottage['type']}", font=("Arial", 10))
            type_label.grid(row=2, column=0, sticky="w", columnspan=2)

            capacity_label = ttk.Label(card_frame, text=f"Capacity: {cottage['capacity']}", font=("Arial", 10))
            capacity_label.grid(row=3, column=0, sticky="w", columnspan=2)

            price_label = ttk.Label(card_frame, text=f"Price: ${cottage['price']:.2f}", font=("Arial", 10))
            price_label.grid(row=4, column=0, sticky="w", columnspan=2)

            description_label = ttk.Label(card_frame, text=f"Description: {cottage['description']}", font=("Arial", 10), wraplength=200)
            description_label.grid(row=5, column=0, sticky="w", pady=(5, 0), columnspan=2)

            id = cottage['cottage_id']
            

            # Display image if available
            image_name = cottage.get('image_name', '')
            if image_name:
                image_path = os.path.join("images", image_name)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    max_width = 250
                    img.thumbnail((max_width, max_width))  # Resize maintaining aspect ratio
                    img_tk = ImageTk.PhotoImage(img)
                    image_label = ttk.Label(card_frame, image=img_tk)
                    image_label.image = img_tk
                    image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

                    select_button = ttk.Button(
                        card_frame, 
                        text="Select",
                        command=lambda cottage_id=id: select_cottage(cottage_id, frame)
                    )
                    select_button.grid(row=6, column=0, columnspan=2, pady=10)


      
        # Update the scrollable area after content is loaded
        cards_frame.update_idletasks()

        # Update scroll region to fit all the content
        canvas.config(scrollregion=canvas.bbox("all"))

        # Adjust row and column configurations to make the grid responsive
        for i in range((len(cottages_halls) + 2) // 3):
            cards_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            cards_frame.grid_columnconfigure(j, weight=1)

    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to retrieve cottages/halls: {e}")
    
def select_cottage(cottage_id, frame):
    """
    This function is triggered when the user selects a cottage.
    It loads the reservation page and updates the cottage ID entry field with the selected cottage's ID.
    
    Args:
    - cottage_id (str): The selected cottage ID.
    - frame (tk.Frame): The current frame for the reservation page.
    """
    
    # Load the reservation frame with the selected cottage ID
    load_reservation(frame, cottage_id)


def load_table_reservation(treeview,conn):
    # Clear existing rows
    for row in treeview.get_children():
        treeview.delete(row)
    
    if conn.is_connected():
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM reservations")
            rows = cursor.fetchall()
            print(rows)
            # Insert data into Treeview
            for row in rows:
                treeview.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading reservations: {err}")
        finally:
            cursor.close()



def add_reservation(reservation_treeview, user_id, cottage_id, start_date, end_date, status, special_requests,conn):
    if conn.is_connected():
        cursor = conn.cursor()
        try:
            # Confirm with the user before proceeding
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to add this reservation?")
            if not confirm:
                return
            
            # Convert start_date and end_date to datetime objects for validation
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Check if the start date is after the end date
            if start_date_obj > end_date_obj:
                messagebox.showerror("Date Error", "End date cannot be before start date.")
                return

            # Check if the given date range overlaps with any existing reservation for the same cottage
            #dec 3 - dec 5
            overlap_query = """
                SELECT COUNT(*) FROM reservations
                WHERE cottage_id = %s
                AND (
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date <= %s AND end_date >= %s) OR
                    (start_date >= %s AND end_date <= %s)
                )
            """
            cursor.execute(overlap_query, (cottage_id, start_date, start_date, end_date, end_date, start_date, end_date))
            overlap_count = cursor.fetchone()[0]

            if overlap_count > 0:
                messagebox.showerror("Date Conflict", "The selected date range is already reserved for this cottage.")
                return

            # Insert the new reservation if there's no conflict
            query = """
                INSERT INTO reservations (user_id, cottage_id, start_date, end_date, status, special_requests)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (user_id, cottage_id, start_date, end_date, status, special_requests)
            cursor.execute(query, data)
            conn.commit()

            messagebox.showinfo("Success", "Reservation added successfully!")
            reservation_treeview.insert('', 'end', values=(None, user_id, cottage_id, start_date, end_date, status, special_requests))
            load_table_reservation(reservation_treeview,conn)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding reservation: {err}")
        
        finally:
            cursor.close()

def update_reservation(reservation_treeview, user_id, cottage_id, start_date, end_date, status, special_requests,conn):
    # Ensure a row is selected before updating
    selected_item = reservation_treeview.selection()  # Get selected item

    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a reservation to update.")
        return  # Exit if no row is selected
    
    

    if conn.is_connected():
        cursor = conn.cursor()
        try:
            reservation_id = reservation_treeview.item(selected_item, 'values')[0]  # Get reservation_id from the selected item
            
            query = """
                UPDATE reservations
                SET user_id = %s, cottage_id = %s, start_date = %s, end_date = %s, status = %s, special_requests = %s
                WHERE reservation_id = %s
            """
            data = (user_id, cottage_id, start_date, end_date, status, special_requests, reservation_id)
            cursor.execute(query, data)
            conn.commit()
            messagebox.showinfo("Success", "Reservation updated successfully!")
            
            # Update the treeview
            reservation_treeview.item(selected_item, values=(reservation_id, user_id, cottage_id, start_date, end_date, status, special_requests))
            
       
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating reservation: {err}")
        finally:
           
            cursor.close()
def delete_selected_reservation(reservation_treeview,conn):
    # Get the selected item from the treeview
    selected_item = reservation_treeview.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a reservation to delete.")
        return

    # Retrieve the reservation_id from the selected row
    reservation_id = reservation_treeview.item(selected_item, 'values')[0]
    if not reservation_id:
        messagebox.showwarning("No ID", "Could not retrieve the reservation ID.")
        return

    # Call the delete function with the correct reservation_id
    delete_reservation(reservation_treeview, reservation_id,conn)


def delete_reservation(reservation_treeview, reservation_id,conn):
    if conn.is_connected():
        cursor = conn.cursor()
        try:
            # Check if reservation_id exists before attempting to delete
            check_query = "SELECT COUNT(*) FROM reservations WHERE reservation_id = %s"
            cursor.execute(check_query, (reservation_id,))
            count = cursor.fetchone()[0]

            if count == 0:
                messagebox.showwarning("Not Found", "The specified reservation does not exist.")
                return

            # Proceed to delete if the reservation exists
            query = "DELETE FROM reservations WHERE reservation_id = %s"
            cursor.execute(query, (reservation_id,))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning("Not Found", "No reservation found with the specified ID. Nothing was deleted.")
            else:
                messagebox.showinfo("Success", "Reservation deleted successfully!")
                load_table_reservation(reservation_treeview,conn)  # Refresh the table after deleting

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting reservation: {err}")
        finally:
            cursor.close()


def load_reservation_data(event, treeview, user_id_entry, cottage_id_entry, start_date_entry, end_date_entry, status_combobox, special_requests_text):
    # Retrieve the selected row in the treeview
    selected_item = event.widget.selection()
    if selected_item:
        item = treeview.item(selected_item)
        reservation_data = item['values']
        
        # Populate the fields with the data from the selected row

        # User ID (Entry)
        user_id_entry.delete(0, ttk.END)
        user_id_entry.insert(0, reservation_data[1])
        
        # Cottage ID (Entry)
        cottage_id_entry.delete(0, ttk.END)
        cottage_id_entry.insert(0, reservation_data[2])
        
        # Start Date (Entry)
        start_date_entry.entry.delete(0, ttk.END)
        start_date_entry.entry.insert(0, reservation_data[3])
        
        # End Date (Entry)
        end_date_entry.entry.delete(0, ttk.END)
        end_date_entry.entry.insert(0, reservation_data[4])
        
        # Status (Combobox)
        status_combobox.set(reservation_data[5])
        
        # Special Requests (Text widget)
        special_requests_text.delete("1.0", ttk.END)
        special_requests_text.insert("1.0", reservation_data[6])
def save_user_to_db(username, password, full_name, sex, contact_info,conn):



    try:

        cursor = conn.cursor()

        # Insert user data into the database
        cursor.execute(
            """
            INSERT INTO users (username, password, full_name, sex, contact_info, role)
            VALUES (%s, %s, %s, %s, %s, 'Guest')
            """,
            (username, password, full_name, sex, contact_info)
        )

        # Commit the changes to the database
        conn.commit()

        # Retrieve the user ID of the newly created user
        user_id = cursor.lastrowid

        # Close the cursor (and connection if necessary)
        cursor.close()
        return user_id

    except Exception as e:
        # Handle any exceptions or errors
        print(f"Error saving user to database: {e}")
        return None

def load_user_registration(frame,conn):
    clear_frame(frame)
    crud_frame = ttk.LabelFrame(frame, text="User Registration")
    crud_frame.grid(padx=10, pady=4, sticky="nsew") 

    # Creating the registration form

    ttk.Label(crud_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5,padx=(30,0))
    username_entry = ttk.Entry(crud_frame)
    username_entry.grid(row=1, column=1, pady=5,)

    ttk.Label(crud_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5,padx=(30,0))
    password_entry = ttk.Entry(crud_frame, show="*")
    password_entry.grid(row=2, column=1, pady=5)

    ttk.Label(crud_frame, text="Full Name:").grid(row=3, column=0, sticky="w", pady=5,padx=(30,0))
    full_name_entry = ttk.Entry(crud_frame)
    full_name_entry.grid(row=3, column=1, pady=5)

    # Dropdown for Sex
    ttk.Label(crud_frame, text="Sex:").grid(row=4, column=0, sticky="w", pady=5,padx=(30,0))
    sex_var = tk.StringVar()
    sex_dropdown = ttk.Combobox(crud_frame, textvariable=sex_var, state="readonly")
    sex_dropdown['values'] = ("Male", "Female")
    sex_dropdown.grid(row=4, column=1, pady=5)
    sex_dropdown.current(0)  # Default to "Male"

    ttk.Label(crud_frame, text="Contact Info:").grid(row=5, column=0, sticky="w", pady=5,padx=(30,0))
    contact_info_entry = ttk.Entry(crud_frame)
    contact_info_entry.grid(row=5, column=1, pady=5)

    # Register button
    ttk.Button(crud_frame, text="Register", command=lambda: register_user(
        frame, username_entry.get(), password_entry.get(), full_name_entry.get(), sex_var.get(), contact_info_entry.get(),conn
    )).grid(row=6, column=0, columnspan=2, pady=10)
    back_to_reservation  = ttk.Button(crud_frame,text="Back To Reservation", command=lambda: load_reservation(frame))
    back_to_reservation.grid(row=0,column=0,pady=30,padx=20)

# Function to register the user
def register_user(frame, username, password, full_name, sex, contact_info,conn):
    # Perform user registration logic here (database logic)
    # Assume there's a function to save the user to the database and get the user ID
    user_id = save_user_to_db(username, password, full_name, sex, contact_info,conn)

    if user_id:
        messagebox.showinfo("Registration Successful", "User registered successfully!")
        # Go back to reservation form with the new user_id pre-filled
        load_reservation(frame, user_id)
    else:
        messagebox.showerror("Registration Error", "Failed to register the user.")

# Function to load the reservation page
def search_user(name, user_id_entry,conn):
    # Connect to the database and search for the user by name
    try:

        cursor = conn.cursor()
        query = "SELECT user_id FROM users WHERE full_name LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{name}%",))
        result = cursor.fetchone()

        if result:
            user_id_entry.delete(0, 'end')  # Clear any existing content
            user_id_entry.insert(0, str(result[0]))  # Insert the found user ID
        else:
            messagebox.showinfo("Search Result", "No account found for the given name.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"An error occurred: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
           

def clear_entries(user_id_entry, cottage_id_entry, start_date_entry, end_date_entry, status_entry, special_requests_text):
 
    user_id_entry.delete(0, ttk.END)
    cottage_id_entry.delete(0, ttk.END)
    start_date_entry.entry.delete(0, ttk.END)
    end_date_entry.entry.delete(0, ttk.END)
    
    # Clear the `Combobox` widget for status (assuming it's a `Combobox`)
    status_entry.set("")
    
    # Clear the `Text` widget for special requests
    special_requests_text.delete("1.0", ttk.END)

def load_reservation(frame, cottage_id=None):
    conn = create_connection()

    clear_frame(frame)

    # Set the updated width for the whole frame
    updated_width = 500

    # Centering the frame using a grid system
    frame.grid_columnconfigure(0, weight=1)  # Make column 0 take up the remaining space
    frame.grid_columnconfigure(1, weight=0)  # Center column for the frames
    frame.grid_columnconfigure(2, weight=1)  # Make column 2 take up the remaining space

    # Frame for reservation inputs (top part)
    crud_reservation = ttk.LabelFrame(frame, text="Reservations", width=updated_width)
    crud_reservation.grid(row=0, column=1, padx=10, pady=4, sticky="ew")
    frame.grid_columnconfigure(1, weight=1)  # Ensures it expands

    # Add User button to open the registration page
    ttk.Button(crud_reservation, text="Add User", command=lambda: load_user_registration(frame,conn)).grid(row=0, column=1, padx=5,  pady=(20,5), sticky="w")

    # Clear button for clearing entry fields
    ttk.Button(crud_reservation, text="Clear", command=lambda: clear_entries(
        user_id_entry, cottage_id_entry, start_date_entry, end_date_entry, status_combobox, special_requests_entry
    )).grid(row=0, column=0, padx=20, pady=(20,5), sticky="w")

    # User ID label and entry
    ttk.Label(crud_reservation, text="User ID:").grid(row=2, column=0, sticky="w", padx=20, pady=5)
    user_id_entry = ttk.Entry(crud_reservation)
    default =  "account name to search"
    user_id_entry.insert(0,default) 

    user_id_entry.grid(row=2, column=1, padx=5, pady=5,sticky='w')
    user_id_entry.bind("<FocusIn>", lambda event: clear_entry(event, user_id_entry,default ))
    user_id_entry.bind("<FocusOut>", lambda event: set_default_text(user_id_entry, default))
    
    ttk.Button(crud_reservation, text="Search Account", command=lambda: search_user(user_id_entry.get(), user_id_entry,conn)).grid(row=2, column=2, padx=5, pady=5)
  
    ttk.Button(crud_reservation, text="Search Cottage", command=lambda: load_avail_cottage_cards(frame,conn)).grid(row=1, column=2, padx=5, pady=5)


    ttk.Label(crud_reservation, text="Cottage ID:").grid(row=1, column=0, sticky="w", padx=20, pady=5)
    cottage_id_entry = ttk.Entry(crud_reservation)
    cottage_id_entry.grid(row=1, column=1, padx=5, pady=5,sticky='w')


    if cottage_id:
        cottage_id_entry.insert(0, str(cottage_id))

  
    ttk.Label(crud_reservation, text="Start Date:").grid(row=3, column=0, sticky="w", padx=20, pady=5)
    start_date_entry = ttk.DateEntry(crud_reservation, width=15, dateformat='%Y-%m-%d')
    start_date_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(crud_reservation, text="End Date:").grid(row=4, column=0, sticky="w", padx=20, pady=5)
    end_date_entry = ttk.DateEntry(crud_reservation, width=15, dateformat='%Y-%m-%d')
    end_date_entry.grid(row=4, column=1, padx=5, pady=20)

    ttk.Label(crud_reservation, text="Status:").grid(row=1, column=5, sticky="w", padx=50, pady=5)
    status_combobox = ttk.Combobox(crud_reservation, values=["Pending", "Confirmed","Cancelled"], state="readonly")
    status_combobox.grid(row=1, column=6, padx=5, pady=5,sticky='w')
    status_combobox.set("Pending") 

    # Special Requests label and entry
    ttk.Label(crud_reservation, text="Special Requests:").grid(row=2, column=5, sticky="n", padx=50, pady=5)
    special_requests_entry = tk.Text(crud_reservation, height=5, wrap="word",width=30)
    special_requests_entry.grid(row=2, column=6,rowspan=3, padx=5, pady=5, sticky="ew")

    # Frame for reservation list (bottom part)
    right_frame = ttk.LabelFrame(frame, text="Reservation List", width=updated_width)
    right_frame.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="nsew")  # Adjusted padding to make the table fill more space
    frame.grid_rowconfigure(1, weight=1)  # Ensures the table expands vertically
    frame.grid_columnconfigure(1, weight=1)  # Ensures it expands

    # CRUD Buttons
    ttk.Button(right_frame, text="Add", command=lambda: add_reservation(
        reservation_treeview, user_id_entry.get(), cottage_id_entry.get(), start_date_entry.entry.get(),
        end_date_entry.entry.get(), status_combobox.get() or "Pending", special_requests_entry.get("1.0", "end").strip(),conn
    )).grid(row=0, column=0, padx=(20,5), pady=(15,10), sticky='w')

    ttk.Button(right_frame, text="Update", command=lambda: update_reservation(
        reservation_treeview, user_id_entry.get(), cottage_id_entry.get(), start_date_entry.entry.get(),
        end_date_entry.entry.get(), status_combobox.get() or "Pending", special_requests_entry.get("1.0", "end").strip(),conn
    )).grid(row=0, column=1,padx=(20,5), pady=(15,10), sticky='w')

    ttk.Button(right_frame, text="Delete", command=lambda: delete_selected_reservation(reservation_treeview,conn)
    ).grid(row=0, column=2, padx=(20,5), pady=(15,10), sticky='w')



    # Treeview to display reservations
    reservation_treeview = ttk.Treeview(
        right_frame, 
        columns=("reservation_id", "user_id", "cottage_id", "start_date", "end_date", "status", "special_requests"),    
        show="headings",
        bootstyle="primary",
        height=15
    )
    reservation_treeview.grid(row=1, column=0, columnspan=20,padx=10, pady=5, sticky="new")
    reservation_treeview.heading("reservation_id", text="Reservation ID")
    reservation_treeview.heading("user_id", text="User ID")
    reservation_treeview.heading("cottage_id", text="Cottage ID")
    reservation_treeview.heading("start_date", text="Start Date")
    reservation_treeview.heading("end_date", text="End Date")
    reservation_treeview.heading("status", text="Status")
    reservation_treeview.heading("special_requests", text="Special Requests")

    # Adjust column widths to reduce spacing
    reservation_treeview.column("reservation_id", width=120)
    reservation_treeview.column("user_id", width=80)
    reservation_treeview.column("cottage_id", width=120)
    reservation_treeview.column("start_date", width=120)
    reservation_treeview.column("end_date", width=120)
    reservation_treeview.column("status", width=120)
    reservation_treeview.column("special_requests", width=300)

    # Vertical scrollbar for treeview
    v_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=reservation_treeview.yview)
    v_scrollbar.grid(row=1, column=21, sticky="nsw")
    reservation_treeview.configure(yscrollcommand=v_scrollbar.set)

    # Bind selection event to load reservation data
    reservation_treeview.bind('<<TreeviewSelect>>', lambda event: load_reservation_data(event, reservation_treeview, user_id_entry, cottage_id_entry, start_date_entry, end_date_entry, status_combobox, special_requests_entry))
    # Load data into Treeview
    load_table_reservation(reservation_treeview,conn)