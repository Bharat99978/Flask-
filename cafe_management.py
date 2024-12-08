from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Ensure the 'uploads' directory exists for saving files
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="mnz.domcloud.co",
        user="fluffy-chest-kie",
        password="1tP6_z14JZ9a_T+zSy",
        database="fluffy_chest_kie_db"
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    conn.close()
    return f"""
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bakery Order Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@10"></script>
</head>
<body class="bg-gray-100 text-gray-800">

    <div class="min-h-screen flex flex-col">
        <!-- Header -->
        <header class="bg-indigo-600 text-white py-4 shadow-md">
            <div class="container mx-auto px-4 flex justify-between items-center">
                <h1 class="text-2xl font-bold">Bakery Order Management</h1>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-4 py-8 flex flex-col space-y-8">
            <!-- Order Form -->
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Add New Order</h2>
                <form id="orderForm" class="space-y-4">
                    <div>
                        <label for="customer_name" class="block text-sm font-medium">Customer Name:</label>
                        <input type="text" id="customer_name" name="customer_name" class="w-full p-2 border border-gray-300 rounded-lg" required>
                    </div>
                    <div>
                        <label for="item" class="block text-sm font-medium">Item:</label>
                        <input type="text" id="item" name="item" class="w-full p-2 border border-gray-300 rounded-lg" required>
                    </div>
                    <div>
                        <label for="quantity" class="block text-sm font-medium">Quantity:</label>
                        <input type="number" id="quantity" name="quantity" class="w-full p-2 border border-gray-300 rounded-lg" required min="1">
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700">
                        Add Order
                    </button>
                </form>
            </section>

            <!-- Orders Table -->
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Orders</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-gray-50 text-left border border-gray-200">
                        <thead class="bg-indigo-600 text-white">
                            <tr>
                                <th class="px-4 py-2">Order ID</th>
                                <th class="px-4 py-2">Customer Name</th>
                                <th class="px-4 py-2">Item</th>
                                <th class="px-4 py-2">Quantity</th>
                                <th class="px-4 py-2">Order Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for order in orders %}
                            <tr class="odd:bg-white even:bg-gray-100">
                                <td class="px-4 py-2">{{ order['Order ID'] }}</td>
                                <td class="px-4 py-2">{{ order['Customer Name'] }}</td>
                                <td class="px-4 py-2">{{ order['Item'] }}</td>
                                <td class="px-4 py-2">{{ order['Quantity'] }}</td>
                                <td class="px-4 py-2">{{ order['Order Date'] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Save Buttons -->
            <section class="flex justify-end space-x-4">
                <button id="saveCSVBtn" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                    Save as CSV
                </button>
                <button id="saveExcelBtn" class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
                    Save as Excel
                </button>
            </section>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-800 text-white py-4">
            <div class="container mx-auto text-center">
                <p>&copy; 2024 Bakery Order Management. All rights reserved.</p>
            </div>
        </footer>
    </div>

    <script>
        $(document).ready(function () {
            // Handle form submission for adding a new order
            $('#orderForm').on('submit', function (e) {
                e.preventDefault();
                
                var formData = $(this).serialize();
                $.post('/add_order', formData, function (response) {
                    if (response.success) {
                        Swal.fire({
                            title: 'Success',
                            text: response.message,
                            icon: 'success'
                        }).then(() => {
                            location.reload(); // Reload the page to show the new order
                        });
                    } else {
                        Swal.fire({
                            title: 'Error',
                            text: response.message,
                            icon: 'error'
                        });
                    }
                });
            });

            // Handle save as CSV
            $('#saveCSVBtn').click(function () {
                $.post('/save_orders', { file_type: 'csv' }, function (response) {
                    Swal.fire({
                        title: response.success ? 'Success' : 'Error',
                        text: response.message,
                        icon: response.success ? 'success' : 'error'
                    }).then(() => {
                        if (response.success) {
                            window.location.href = '/uploads/' + response.file_path.split('/')[1];
                        }
                    });
                });
            });

            // Handle save as Excel
            $('#saveExcelBtn').click(function () {
                $.post('/save_orders', { file_type: 'excel' }, function (response) {
                    Swal.fire({
                        title: response.success ? 'Success' : 'Error',
                        text: response.message,
                        icon: response.success ? 'success' : 'error'
                    }).then(() => {
                        if (response.success) {
                            window.location.href = '/uploads/' + response.file_path.split('/')[1];
                        }
                    });
                });
            });
        });
    </script>

</body>
</html>
    """

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
        cursor.execute('SELECT * FROM orders')
        orders = cursor.fetchall()
        conn.close()

        if not orders:
            raise ValueError("No orders to save.")

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