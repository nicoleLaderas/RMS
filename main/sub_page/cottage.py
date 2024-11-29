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

def create_connection():
    connection = mysql.connector.connect(
        user='root',
        password='', 
        port=3306,
        host='localhost',
        database='rms_db'  
    )
    return connection
conn = create_connection()
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def load_cottage_cards(frame):
    clear_frame(frame)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", padx=10, pady=10)

    go_back_button = ttk.Button(header_frame, text="Go Back", command=lambda: load_cottage(frame))
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

    try:
       
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cottages_halls")
        cottages_halls = cursor.fetchall()
        

        for index, cottage in enumerate(cottages_halls):
         
            card_frame = ttk.Frame(cards_frame, bootstyle="light", padding=10, relief="raised", width=320, height=450)
            card_frame.grid_propagate(False)  
            
           
            row = index // 3  
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

    
            image_name = cottage.get('image_name', '')
            if image_name:
                image_path = os.path.join("images", image_name)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    max_width = 250
                    img.thumbnail((max_width, max_width))  
                    img_tk = ImageTk.PhotoImage(img)
                    image_label = ttk.Label(card_frame, image=img_tk)
                    image_label.image = img_tk
                    image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

            
            update_button = ttk.Button(card_frame, text="Update", command=lambda c=cottage: update_cottage_hall(frame, c))
            update_button.grid(row=6, column=0, pady=10, padx=5, sticky="e")

            delete_button = ttk.Button(card_frame, text="Delete", command=lambda c=cottage: delete_cottage(frame, c))
            delete_button.grid(row=6, column=1, pady=10, padx=5, sticky="w")

        cards_frame.update_idletasks()

        canvas.config(scrollregion=canvas.bbox("all"))

        # Adjust row and column configurations to make the grid responsive
        for i in range((len(cottages_halls) + 2) // 3):
            cards_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            cards_frame.grid_columnconfigure(j, weight=1)

    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to retrieve cottages/halls: {e}")
def update_cottage_hall(frame, cottage):
    clear_frame(frame)

    # Create form fields to update the selected cottage
    title_label = ttk.Label(frame, text="Update Cottage/Hall", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Variables to store form data
    name_var = tk.StringVar(value=cottage['name'])
    type_var = tk.StringVar(value=cottage['type'])
    capacity_var = tk.IntVar(value=cottage['capacity'])
    price_var = tk.DoubleVar(value=cottage['price'])
    description_var = tk.StringVar(value=cottage['description'])
    
    # Variable to store the path of the new image if selected
    selected_image_path_var = tk.StringVar(value="")  # Default to an empty string for no image

    # Form fields for updating
    name_entry = ttk.Entry(frame, textvariable=name_var)
    name_entry.pack(pady=5)
    
    type_entry = ttk.Entry(frame, textvariable=type_var)
    type_entry.pack(pady=5)
    
    capacity_entry = ttk.Entry(frame, textvariable=capacity_var)
    capacity_entry.pack(pady=5)
    
    price_entry = ttk.Entry(frame, textvariable=price_var)
    price_entry.pack(pady=5)
    
    description_entry = ttk.Entry(frame, textvariable=description_var, width=50)
    description_entry.pack(pady=5)

    # Only show the image field if the user wants to update the image
    image_name_entry = ttk.Entry(frame, textvariable=selected_image_path_var, state="readonly", width=50)
    image_name_entry.pack(pady=5)

    # Function to select a new image
    def select_new_image():
        new_image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")],
            title="Select New Image"
        )
        if new_image_path:
            selected_image_path_var.set(new_image_path)  # Set the new image path

    # Button to select a new image
    image_button = ttk.Button(frame, text="Select New Image", command=select_new_image)
    image_button.pack(pady=10)

    # Get the cottage_id using .get() to access the correct key safely
    cottage_id = cottage.get('cottage_id')

    # Update and Cancel buttons
    update_btn = ttk.Button(frame, text="Update", command=lambda: update_cottage_in_db(
        frame, 
        cottage_id,  # Now using cottage_id, safely retrieved using .get()
        name_var.get(), 
        type_var.get(), 
        capacity_var.get(), 
        price_var.get(), 
        description_var.get(), 
        selected_image_path_var.get() if selected_image_path_var.get() else None  # Only pass image if selected, else pass None
    ))
    update_btn.pack(pady=10)

    cancel_btn = ttk.Button(frame, text="Cancel", command=lambda: load_cottage_cards(frame))
    cancel_btn.pack(pady=5)
def delete_cottage(frame, cottage):
    try:
        # Confirm the deletion action
        result = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete '{cottage['name']}'?")
        if result:
            # Connect to the database
    
            cursor = conn.cursor()
            cottage_id = cottage.get('cottage_id')  # Access the correct key
            
            if cottage_id is None:
                messagebox.showerror("Error", "Cottage ID not found.")
                return

            # Query to get the image file name associated with this cottage
            image_query = "SELECT image_name FROM cottages_halls WHERE cottage_id = %s"
            cursor.execute(image_query, (cottage_id,))
            image_path = cursor.fetchone()

            if image_path:
                image_name = image_path[0]
                image_file_path = os.path.join("images", image_name)  # Assuming images are in 'images' folder
                
                # If the image exists, try to delete it
                if os.path.exists(image_file_path):
                    try:
                        os.remove(image_file_path)  # Delete the image file
                        print(f"Image '{image_file_path}' has been deleted.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete image: {e}")
                        return
                else:
                    print(f"Image file '{image_file_path}' not found.")
            
            # Delete the cottage record from the database
            delete_query = "DELETE FROM cottages_halls WHERE cottage_id = %s"
            cursor.execute(delete_query, (cottage_id,))
            
            # Commit the changes and close the connection
            conn.commit()
          

            # Inform the user that the cottage has been deleted successfully
            messagebox.showinfo("Success", f"'{cottage['name']}' has been deleted.")
            
            # Refresh the content after deletion
            load_cottage_cards(frame)  # Reload the list after deletion
        else:
            # If the user cancels the deletion, do nothing
            return
    except mysql.connector.Error as db_error:
        messagebox.showerror("Database Error", f"Failed to delete cottage: {db_error}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
def update_cottage_in_db(frame, cottage_id, name, type_, capacity, price, description, new_image_path):
    try:
        # Connect to the database
        cursor = conn.cursor()

        # Fetch the current image name from the database
        cursor.execute("SELECT image_name FROM cottages_halls WHERE cottage_id = %s", (cottage_id,))
        current_image = cursor.fetchone()
        current_image_name = current_image[0] if current_image else None  # Access image name

        if new_image_path:
            # Handle new image
            new_image_name = os.path.basename(new_image_path)
            new_image_destination = os.path.join("images", new_image_name)

            # If there's an existing image, delete it first
            if current_image_name:
                old_image_path = os.path.join("images", current_image_name)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Copy the new image to the 'images' directory
            shutil.copy(new_image_path, new_image_destination)

            # Update the record with the new image and other fields
            cursor.execute(
                """
                UPDATE cottages_halls 
                SET name = %s, type = %s, capacity = %s, price = %s, description = %s, image_name = %s 
                WHERE cottage_id = %s
                """,
                (name, type_, capacity, price, description, new_image_name, cottage_id)
            )
        else:
            # If no new image is provided, only update the text fields
            cursor.execute(
                """
                UPDATE cottages_halls 
                SET name = %s, type = %s, capacity = %s, price = %s, description = %s 
                WHERE cottage_id = %s
                """,
                (name, type_, capacity, price, description, cottage_id)
            )

        # Commit the changes and close the connection
        conn.commit()
       
        messagebox.showinfo("Success", "Cottage/Hall updated successfully.")
        load_cottage_cards(frame)  # Reload the list to reflect the changes
    except conn.Error as db_error:
        messagebox.showerror("Database Error", f"Failed to update cottage: {db_error}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def load_cottage(frame):
    clear_frame(frame)
    cottage_frame = ttk.LabelFrame(frame, text="Reservations")
    cottage_frame.grid(row=0, column=1, padx=10, pady=4, sticky="ew")
    ttk.Label(cottage_frame, text="Add New Cottage or Hall", font=("Arial", 20), bootstyle="primary").pack(pady=20)

    # Fields for data entry
    form_frame = ttk.Frame(cottage_frame, bootstyle="light")
    form_frame.pack(pady=30, padx=30, fill="x")

    # Name Entry
    ttk.Label(form_frame, text="Name", font=("Arial", 12)).grid(row=0, column=0, pady=5, padx=5, sticky="e")
    name_entry = ttk.Entry(form_frame, font=("Arial", 12))
    name_entry.grid(row=0, column=1, pady=5, padx=5, sticky="w")

    # Type Entry (Dropdown)
    ttk.Label(form_frame, text="Type", font=("Arial", 12)).grid(row=1, column=0, pady=5, padx=5, sticky="e")
    type_var = ttk.StringVar()
    type_combobox = ttk.Combobox(form_frame, textvariable=type_var, values=["Cottage", "Hall"], state="readonly", font=("Arial", 12))
    type_combobox.grid(row=1, column=1, pady=5, padx=5, sticky="w")
    type_combobox.current(0)  # Default to "Cottage"

    # Capacity Entry
    ttk.Label(form_frame, text="Capacity", font=("Arial", 12)).grid(row=2, column=0, pady=5, padx=5, sticky="e")
    capacity_entry = ttk.Entry(form_frame, font=("Arial", 12))
    capacity_entry.grid(row=2, column=1, pady=5, padx=5, sticky="w")

    # Price Entry
    ttk.Label(form_frame, text="Price ($)", font=("Arial", 12)).grid(row=3, column=0, pady=5, padx=5, sticky="e")
    price_entry = ttk.Entry(form_frame, font=("Arial", 12))
    price_entry.grid(row=3, column=1, pady=5, padx=5, sticky="w")

    # Description Entry
    ttk.Label(form_frame, text="Description", font=("Arial", 12)).grid(row=4, column=0, pady=5, padx=5, sticky="e")
    description_entry = ttk.Entry(form_frame, font=("Arial", 12), width=50)
    description_entry.grid(row=4, column=1, pady=5, padx=5, sticky="w")
    image_path_var = ttk.StringVar()
    ttk.Label(form_frame, text="Image", font=("Arial", 12)).grid(row=5, column=0, pady=(3,40), padx=5, sticky="e")
    image_entry = ttk.Entry(form_frame, textvariable=image_path_var, font=("Arial", 12), state="readonly")
    image_entry.grid(row=5, column=1, pady=(3,40), padx=5, sticky="w")

    def select_image():
        """Open file dialog to select an image."""
        file_path = filedialog.askopenfilename(
            title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            image_path_var.set(file_path)

    image_button = ttk.Button(form_frame, text="Browse", command=select_image)
    image_button.grid(row=5, column=2, pady=(3,40), padx=5)

    def save_cottage():
        """Save new cottage/hall details."""
        name = name_entry.get()
        cottage_type = type_var.get()
        capacity = capacity_entry.get()
        price = price_entry.get()
        description = description_entry.get()
        image_name = os.path.basename(image_path_var.get())

        if not all([name, cottage_type, capacity, price, description]):
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return
        
        try:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO cottages_halls (name, type, capacity, price, description, image_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, cottage_type, capacity, price, description, image_name))

            conn.commit()
           
            # Optionally, move the image to a central folder
            if image_path_var.get():
                shutil.copy(image_path_var.get(), os.path.join("images", image_name))

            messagebox.showinfo("Success", "New Cottage/Hall added successfully.")
            load_cottage_cards(frame)  # Reload the cottage cards display
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save cottage: {e}")

    save_button = ttk.Button(cottage_frame, text="Save Cottage", command=save_cottage, bootstyle="primary")
    save_button.pack(pady=10)

    view_cards_button = ttk.Button(cottage_frame, text="View Cottage Cards", command=lambda: load_cottage_cards(frame), bootstyle="primary")
    view_cards_button.pack(pady=30)

