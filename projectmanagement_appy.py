# app.py
import streamlit as st
import pandas as pd
from pymongo import MongoClient
try:
    import pymongo
    print("pymongo is installed")
except ModuleNotFoundError:
    print("pymongo is not installed")

git add requirements.txt
git commit -m "Added pymongo to requirements"
git push origin main  # or the branch you are using

# MongoDB connection
client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/test?retryWrites=true&w=majority")
db = client['construction']
inventory_collection = db['inventory']

# Streamlit App
st.title("Inventory Management")

# Inventory Form
item_id = st.text_input("Item ID")
item_name = st.text_input("Item Name")
quantity = st.number_input("Quantity", min_value=0)
date_of_arrival = st.date_input("Date of Arrival")
supplier_details = st.text_input("Supplier Details")

if st.button("Add Item"):
    inventory_item = {
        "item_id": item_id,
        "item_name": item_name,
        "quantity": quantity,
        "date_of_arrival": date_of_arrival,
        "supplier_details": supplier_details
    }
    inventory_collection.insert_one(inventory_item)
    st.success("Item added to inventory")

# Display Inventory
st.subheader("Inventory List")
inventory_data = pd.DataFrame(list(inventory_collection.find()))
st.write(inventory_data)

# app.py (continued)

st.title("Attendance Register")

# Attendance Form
worker_id = st.text_input("Worker ID")
worker_name = st.text_input("Worker Name")
date = st.date_input("Date")
time_of_arrival = st.time_input("Time of Arrival")
time_of_departure = st.time_input("Time of Departure")

if st.button("Record Attendance"):
    attendance_record = {
        "worker_id": worker_id,
        "worker_name": worker_name,
        "date": date,
        "time_of_arrival": time_of_arrival,
        "time_of_departure": time_of_departure
    }
    db.attendance.insert_one(attendance_record)
    st.success("Attendance recorded")

# Display Attendance
st.subheader("Attendance Records")
attendance_data = pd.DataFrame(list(db.attendance.find()))
st.write(attendance_data)

# app.py (continued)

st.title("Payment Tracking")

# Payment Form
payment_worker_id = st.text_input("Worker ID", key="payment_worker_id")
payment_worker_name = st.text_input("Worker Name", key="payment_worker_name")
payment_date = st.date_input("Payment Date")
amount_paid = st.number_input("Amount Paid", min_value=0.0)
payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money"])

if st.button("Record Payment"):
    payment_record = {
        "worker_id": payment_worker_id,
        "worker_name": payment_worker_name,
        "payment_date": payment_date,
        "amount_paid": amount_paid,
        "payment_method": payment_method
    }
    db.payments.insert_one(payment_record)
    st.success("Payment recorded")

# Display Payments
st.subheader("Payment Records")
payment_data = pd.DataFrame(list(db.payments.find()))
st.write(payment_data)

