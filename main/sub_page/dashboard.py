import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import mysql.connector


# Database Connection
def create_connection():
    connection = mysql.connector.connect(
        user='root',
        password='', 
        port=3306,
        host='localhost',
        database='rms_db'  
    )
    return connection





# Clear frame function
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


# Fetch summary data
def fetch_summary(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch data counts
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) AS total_cottages FROM cottages_halls WHERE type = 'Cottage'")
        total_cottages = cursor.fetchone()['total_cottages']
        
        cursor.execute("SELECT COUNT(*) AS total_halls FROM cottages_halls WHERE type = 'Hall'")
        total_halls = cursor.fetchone()['total_halls']
        
        cursor.execute("SELECT COUNT(*) AS pending_reservations FROM reservations WHERE status = 'Pending'")
        pending_reservations = cursor.fetchone()['pending_reservations']
        
        cursor.execute("SELECT COUNT(*) AS confirmed_reservations FROM reservations WHERE status = 'Confirmed'")
        confirmed_reservations = cursor.fetchone()['confirmed_reservations']
        
        cursor.execute("SELECT COUNT(*) AS cancelled_reservations FROM reservations WHERE status = 'Cancelled'")
        cancelled_reservations = cursor.fetchone()['cancelled_reservations']
        
        cursor.execute("SELECT SUM(amount) AS total_revenue FROM transactions WHERE status = 'Confirmed'")
        total_revenue = cursor.fetchone()['total_revenue'] or 0.00

        return {
            "total_users": total_users,
            "total_cottages": total_cottages,
            "total_halls": total_halls,
            "pending_reservations": pending_reservations,
            "confirmed_reservations": confirmed_reservations,
            "cancelled_reservations": cancelled_reservations,
            "total_revenue": total_revenue
        }
    except Exception as e:
        print(f"Error fetching summary: {e}")
        return {}

def load_dashboard(frame):
    conn = create_connection()
    clear_frame(frame)

    # Dashboard Title
    ttk.Label(frame, text="Dashboard", font=("Arial", 20), bootstyle="success").pack(pady=20)

    # Fetch data
    summary = fetch_summary(conn)
    
    # Create a grid layout for the summary boxes
    dashboard_frame = ttk.Frame(frame)
    dashboard_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    # Create individual frames for each box
    # Users Frame
    users_frame = ttk.Frame(dashboard_frame, bootstyle="primary")
    users_frame.grid(row=0, column=0, padx=10, pady=10, sticky=NSEW)
    ttk.Label(users_frame, bootstyle="inverse-primary", text=f"Total Users", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(users_frame, text=f"{summary['total_users']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-primary").pack(expand=True)

    # Cottages Frame
    cottages_frame = ttk.Frame(dashboard_frame, bootstyle="info")
    cottages_frame.grid(row=0, column=1, padx=10, pady=10, sticky=NSEW)
    ttk.Label(cottages_frame, bootstyle="inverse-info", text=f"Cottages", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(cottages_frame, text=f"{summary['total_cottages']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-info").pack(expand=True)

    # Halls Frame
    halls_frame = ttk.Frame(dashboard_frame, bootstyle="info")
    halls_frame.grid(row=0, column=2, padx=10, pady=10, sticky=NSEW)
    ttk.Label(halls_frame, bootstyle="inverse-info", text=f"Halls", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(halls_frame, text=f"{summary['total_halls']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-info").pack(expand=True)

    # Pending Reservations Frame
    pending_frame = ttk.Frame(dashboard_frame, bootstyle="warning")
    pending_frame.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)
    ttk.Label(pending_frame,bootstyle="inverse-warning", text=f"Pending Reservations", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(pending_frame, text=f"{summary['pending_reservations']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-warning").pack(expand=True)

    # Confirmed Reservations Frame
    confirmed_frame = ttk.Frame(dashboard_frame, bootstyle="success")
    confirmed_frame.grid(row=1, column=1, padx=10, pady=10, sticky=NSEW)
    ttk.Label(confirmed_frame,bootstyle="inverse-success", text=f"Confirmed Reservations", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(confirmed_frame, text=f"{summary['confirmed_reservations']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-success").pack(expand=True)

    # Cancelled Reservations Frame
    cancelled_frame = ttk.Frame(dashboard_frame, bootstyle="danger")
    cancelled_frame.grid(row=1, column=2, padx=10, pady=10, sticky=NSEW)
    ttk.Label(cancelled_frame,bootstyle="inverse-danger", text=f"Cancelled Reservations", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(cancelled_frame, text=f"{summary['cancelled_reservations']}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-danger").pack(expand=True)

    # Total Revenue Frame (spanning across the bottom row)
    revenue_frame = ttk.Frame(dashboard_frame, bootstyle="secondary")
    revenue_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=EW)
    ttk.Label(revenue_frame,bootstyle="inverse-secondary", text=f"Total Revenue", font=("Arial", 12)).pack(pady=(20,0))
    ttk.Label(revenue_frame, text=f"${summary['total_revenue']:.2f}", font=("Arial", 16, "bold"), 
              bootstyle="inverse-secondary").pack(expand=True)

    # Configure grid weights to make it responsive
    for i in range(3):
        dashboard_frame.columnconfigure(i, weight=1)
    for i in range(2):
        dashboard_frame.rowconfigure(i, weight=1)
