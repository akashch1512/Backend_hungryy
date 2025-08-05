import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, MenuItem, Order, OrderItem, Booking, Payment
import razorpay
from datetime import datetime
from flask_migrate import Migrate




# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize Database
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Razorpay
razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)

# --- API Endpoints ---

# Menu API
@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Returns the entire menu, grouped by category."""
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    menu_by_category = {}
    for item in menu_items:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item.to_dict())
    return jsonify(menu_by_category)

# Order Placement API
@app.route('/api/orders', methods=['POST'])
def place_order():
    """Places a new order and stores it in the database."""
    data = request.get_json()

    # Basic validation
    if not all(k in data for k in ['customer_name', 'customer_phone', 'items', 'total_price']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_order = Order(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_email=data.get('customer_email'),
        delivery_address=data.get('delivery_address'),
        total_price=data['total_price']
    )

    for item_data in data['items']:
        menu_item = MenuItem.query.filter_by(name=item_data['name']).first()
        if menu_item:
            order_item = OrderItem(
                menu_item_id=menu_item.id,
                quantity=item_data['quantity'],
                price=menu_item.price
            )
            new_order.order_items.append(order_item)

    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.id}), 201

# Table Booking API
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Creates a new table booking."""
    data = request.get_json()

    if not all(k in data for k in ['customer_name', 'customer_phone', 'booking_date', 'booking_time', 'number_of_people']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_booking = Booking(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        booking_date=datetime.strptime(data['booking_date'], '%Y-%m-%d').date(),
        booking_time=datetime.strptime(data['booking_time'], '%H:%M').time(),
        number_of_people=data['number_of_people']
    )

    db.session.add(new_booking)
    db.session.commit()

    return jsonify({'message': 'Booking created successfully', 'booking_id': new_booking.id}), 201

# Payment API - Create Razorpay Order
@app.route('/api/payments/create_order', methods=['POST'])
def create_razorpay_order():
    """Creates a Razorpay order and returns the order ID."""
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400

    amount_in_paise = int(data['amount'] * 100)

    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'receipt': f'order_rcptid_{int(datetime.now().timestamp())}',
        'payment_capture': 1
    }
    
    try:
        razorpay_order = razorpay_client.order.create(order_data)
        return jsonify({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': os.getenv('RAZORPAY_KEY_ID')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Payment API - Verify Payment
@app.route('/api/payments/verify', methods=['POST'])
def verify_payment():
    """Verifies the Razorpay payment and updates the order status."""
    data = request.get_json()
    if not all(k in data for k in ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature', 'order_id']):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update order and payment status in DB
        order = Order.query.get(data['order_id'])
        if order:
            order.status = 'Confirmed'
            
            payment = Payment(
                order_id=order.id,
                payment_method='Razorpay',
                razorpay_payment_id=data['razorpay_payment_id'],
                razorpay_order_id=data['razorpay_order_id'],
                razorpay_signature=data['razorpay_signature'],
                amount=order.total_price,
                status='Success'
            )
            db.session.add(payment)
            db.session.commit()

            return jsonify({'message': 'Payment successful and order confirmed'})
        else:
            return jsonify({'error': 'Order not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# --- Admin Panel APIs ---

@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders():
    """Returns all orders for the admin panel."""
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Updates the status of an order (e.g., 'Delivered', 'Cancelled')."""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    order = Order.query.get(order_id)
    if order:
        order.status = data['status']
        db.session.commit()
        return jsonify({'message': f'Order {order_id} status updated to {data["status"]}'})
    else:
        return jsonify({'error': 'Order not found'}), 404

@app.route('/api/admin/bookings', methods=['GET'])
def get_all_bookings():
    """Returns all bookings for the admin panel."""
    bookings = Booking.query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
    return jsonify([booking.to_dict() for booking in bookings])


if __name__ == '__main__':
    with app.app_context():
        print("Creating DB Tables...")
        db.create_all()
        print("Tables should be created now.")
    app.run(debug=True)
