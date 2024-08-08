import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('inventory_management.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        item_id TEXT PRIMARY KEY,
        item_name TEXT,
        quantity INTEGER,
        date_of_arrival DATE,
        supplier_details TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS inventory_transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        transaction_type TEXT,  -- 'in' or 'out'
        quantity INTEGER,
        transaction_date DATE,
        FOREIGN KEY(item_id) REFERENCES inventory(item_id)
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        worker_id TEXT PRIMARY KEY,
        worker_name TEXT,
        date DATE,
        time_of_arrival TIME,
        time_of_departure TIME
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        worker_id TEXT,
        worker_name TEXT,
        payment_date DATE,
        amount_paid REAL,
        payment_method TEXT
    )
''')

# Streamlit App
st.title("Inventory Management")

# Inventory Form
item_id = st.text_input("Item ID")
item_name = st.text_input("Item Name")
quantity = st.number_input("Quantity", min_value=0)
transaction_type = st.selectbox("Transaction Type", ["in", "out"])  # Select In or Out
date_of_arrival = st.date_input("Date of Transaction")
supplier_details = st.text_input("Supplier Details")

if st.button("Record Transaction"):
    with conn:
        # Insert or update the inventory item
        if transaction_type == 'in':
            c.execute('''
                INSERT OR IGNORE INTO inventory (item_id, item_name, quantity, date_of_arrival, supplier_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, item_name, quantity, date_of_arrival, supplier_details))
            c.execute('''
                UPDATE inventory SET quantity = quantity + ? WHERE item_id = ?
            ''', (quantity, item_id))
        elif transaction_type == 'out':
            # Ensure the item exists and has enough quantity for the out transaction
            current_quantity = c.execute('SELECT quantity FROM inventory WHERE item_id = ?', (item_id,)).fetchone()
            if current_quantity and current_quantity[0] >= quantity:
                c.execute('''
                    UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?
                ''', (quantity, item_id))
            else:
                st.error("Not enough inventory to remove this quantity.")
                conn.rollback()
                conn.commit()
                conn.close()
                st.stop()
        
        # Record the transaction
        c.execute('''
            INSERT INTO inventory_transactions (item_id, transaction_type, quantity, transaction_date)
            VALUES (?, ?, ?, ?)
        ''', (item_id, transaction_type, quantity, date_of_arrival))
    st.success("Transaction recorded successfully")

# Display Inventory Balance
st.subheader("Inventory Balance")
try:
    inventory_data = pd.read_sql_query('''
        SELECT i.item_id, i.item_name, 
               SUM(CASE WHEN t.transaction_type = 'in' THEN t.quantity ELSE 0 END) -
               SUM(CASE WHEN t.transaction_type = 'out' THEN t.quantity ELSE 0 END) AS balance
        FROM inventory i
        LEFT JOIN inventory_transactions t ON i.item_id = t.item_id
        GROUP BY i.item_id, i.item_name
    ''', conn)
    st.write(inventory_data)
except Exception as e:
    st.error(f"An error occurred while fetching inventory data: {e}")

# Attendance Section
st.title("Attendance Register")

# Attendance Form
worker_id = st.text_input("Worker ID", key="attendance_worker_id")
worker_name = st.text_input("Worker Name", key="attendance_worker_name")
date = st.date_input("Date", key="attendance_date")
time_of_arrival = st.time_input("Time of Arrival")
time_of_departure = st.time_input("Time of Departure")

if st.button("Record Attendance"):
    with conn:
        c.execute('''
            INSERT OR REPLACE INTO attendance (worker_id, worker_name, date, time_of_arrival, time_of_departure)
            VALUES (?, ?, ?, ?, ?)
        ''', (worker_id, worker_name, date, time_of_arrival, time_of_departure))
    st.success("Attendance recorded")

# Display Attendance
st.subheader("Attendance Records")
attendance_data = pd.read_sql_query("SELECT * FROM attendance", conn)
st.write(attendance_data)

# Payment Section
st.title("Payment Tracking")

# Payment Form
payment_worker_id = st.text_input("Worker ID", key="payment_worker_id")
payment_worker_name = st.text_input("Worker Name", key="payment_worker_name")
payment_date = st.date_input("Payment Date", key="payment_date")
amount_paid = st.number_input("Amount Paid", min_value=0.0)
payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money"])

if st.button("Record Payment"):
    with conn:
        c.execute('''
            INSERT INTO payments (worker_id, worker_name, payment_date, amount_paid, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (payment_worker_id, payment_worker_name, payment_date, amount_paid, payment_method))
    st.success("Payment recorded")

# Display Payments
st.subheader("Payment Records")
payment_data = pd.read_sql_query("SELECT * FROM payments", conn)
st.write(payment_data)

# Signature Section
st.title("Signature Section")

signature_image = st.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"])

if signature_image:
    st.image(signature_image, caption="Uploaded Signature", use_column_width=True)

# Close the connection when the app is stopped
conn.close()
