import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import mysql.connector
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# Ensure the 'uploads' directory exists for saving files
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="mnz.domcloud.co",  # Your database host
        user="fluffy-chest-kie",  # Your MySQL username
        password="1tP6_z14JZ9a_T+zSy",  # Your MySQL password
        database="fluffy_chest_kie_db"  # Your MySQL database name
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM orders')  # Get all orders from the 'orders' table
    orders = cursor.fetchall()
    conn.close()

    # Map database column names to template-friendly keys
    for order in orders:
        order['Order ID'] = order['order_id']
        order['Customer Name'] = order['customer_name']
        order['Item'] = order['item']
        order['Quantity'] = order['quantity']
        order['Order Date'] = order['order_date']

    return render_template('index.html', orders=orders)

@app.route('/add_order', methods=['POST'])
def add_order():
    customer_name = request.form['customer_name']
    item = request.form['item']
    quantity = int(request.form['quantity'])
    
    if not customer_name or not item or quantity <= 0:
        return jsonify({"success": False, "message": "All fields must be filled, and quantity must be positive."})
    
    order_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (customer_name, item, quantity, order_date) VALUES (%s, %s, %s, %s)',
                   (customer_name, item, quantity, order_date))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Order added successfully!"})

@app.route('/save_orders', methods=['POST'])
def save_orders():
    try:
        file_type = request.form['file_type']
        now = datetime.now()
        filename = f"bakery_orders_{now.strftime('%Y%m%d_%H%M%S')}"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM orders')  # Fetch orders from the database
        orders = cursor.fetchall()
        conn.close()

        if not orders:
            raise ValueError("No orders to save.")

        # Convert orders to DataFrame for export
        df = pd.DataFrame(orders)

        if file_type == "csv":
            filename += ".csv"
            file_path = os.path.join('uploads', filename)
            df.to_csv(file_path, index=False)
        elif file_type == "excel":
            filename += ".xlsx"
            file_path = os.path.join('uploads', filename)
            df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            raise ValueError("Invalid file type.")

        return jsonify({"success": True, "message": f"Orders saved as '{filename}'", "file_path": file_path})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to save file: {e}"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == "__main__":
    app.run(debug=True)