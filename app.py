import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, MenuItem, Order, OrderItem, Booking, Payment
import razorpay
from datetime import datetime, timedelta
from flask_migrate import Migrate
from sqlalchemy import func

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

with app.app_context():
    print("Creating DB Tables if they don't exist...")
    db.create_all()
    print("Tables should be created now.")

# Initialize Razorpay
razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)

# --- CUSTOMER API ENDPOINTS ---

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Returns the available menu for customers, grouped by category."""
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    menu_by_category = {}
    for item in menu_items:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item.to_dict())
    return jsonify(menu_by_category)

@app.route('/api/orders', methods=['POST'])
def place_order():
    """Places a new order and stores it in the database."""
    data = request.get_json()
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
            order_item = OrderItem(menu_item_id=menu_item.id, quantity=item_data['quantity'], price=menu_item.price)
            new_order.order_items.append(order_item)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.id}), 201

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

@app.route('/api/payments/create_order', methods=['POST'])
def create_razorpay_order():
    """Creates a Razorpay order for payment."""
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

@app.route('/api/payments/verify', methods=['POST'])
def verify_payment():
    """Verifies a Razorpay payment and updates the order."""
    data = request.get_json()
    if not all(k in data for k in ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature', 'order_id']):
        return jsonify({'error': 'Missing required fields for verification'}), 400

    try:
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        razorpay_client.utility.verify_payment_signature(params_dict)

        order = Order.query.get(data['order_id'])
        if order:
            order.status = 'Confirmed'
            payment = Payment(
                order_id=order.id, payment_method='Razorpay',
                razorpay_payment_id=data['razorpay_payment_id'],
                razorpay_order_id=data['razorpay_order_id'],
                razorpay_signature=data['razorpay_signature'],
                amount=order.total_price, status='Success'
            )
            db.session.add(payment)
            db.session.commit()
            return jsonify({'message': 'Payment successful and order confirmed'})
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- ADMIN PANEL API ENDPOINTS ---

@app.route('/api/admin/menu', methods=['GET'])
def get_admin_menu():
    """Returns the entire menu for the admin panel."""
    menu_items = MenuItem.query.order_by(MenuItem.category, MenuItem.name).all()
    return jsonify([item.to_dict() for item in menu_items])

@app.route('/api/admin/menu', methods=['POST'])
def add_menu_item():
    """Adds a new item to the menu."""
    data = request.get_json()
    if not all(k in data for k in ['name', 'price', 'category']):
        return jsonify({'error': 'Missing required fields: name, price, category'}), 400
    
    new_item = MenuItem(
        name=data['name'], description=data.get('description', ''), price=float(data['price']),
        image_url=data.get('image_url', ''), category=data['category'], is_veg=data.get('is_veg', True),
        is_available=data.get('is_available', True)
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route('/api/admin/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    """Updates an existing menu item."""
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = float(data.get('price', item.price))
    item.image_url = data.get('image_url', item.image_url)
    item.category = data.get('category', item.category)
    item.is_veg = data.get('is_veg', item.is_veg)
    item.is_available = data.get('is_available', item.is_available)
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/api/admin/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """Deletes a menu item."""
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Menu item deleted successfully'}), 200

@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders():
    """Returns all orders for the admin panel."""
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Updates the status of an order."""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    order.status = data['status']
    db.session.commit()
    return jsonify({'message': f'Order {order_id} status updated to {data["status"]}'})

@app.route('/api/admin/bookings', methods=['GET'])
def get_all_bookings():
    """Returns all bookings for the admin panel."""
    bookings = Booking.query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
    return jsonify([booking.to_dict() for booking in bookings])

@app.route('/api/admin/reports', methods=['GET'])
def get_reports():
    """Generates sales reports based on a given period."""
    period = request.args.get('period', 'daily')
    date_str = request.args.get('date')

    end_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    
    if period == 'daily':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_date = end_date - timedelta(days=6)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=29)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return jsonify({'error': 'Invalid period specified'}), 400

    orders = Order.query.filter(Order.order_date >= start_date, Order.order_date <= end_date).all()
    
    total_orders = len(orders)
    total_revenue = sum(order.total_price for order in orders)
    total_items_sold = sum(item.quantity for order in orders for item in order.order_items)
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0

    top_items_query = db.session.query(
        MenuItem.name, func.sum(OrderItem.quantity).label('total_quantity')
    ).join(OrderItem.menu_item).join(Order).filter(
        Order.order_date >= start_date, Order.order_date <= end_date
    ).group_by(MenuItem.name).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    top_selling_items = [{'name': name, 'quantity': qty} for name, qty in top_items_query]

    peak_times = {'Late Night': 0, 'Morning': 0, 'Afternoon': 0, 'Evening': 0}
    for order in orders:
        hour = order.order_date.hour
        if 6 <= hour < 12: peak_times['Morning'] += 1
        elif 12 <= hour < 18: peak_times['Afternoon'] += 1
        elif 18 <= hour < 24: peak_times['Evening'] += 1
        else: peak_times['Late Night'] += 1

    return jsonify({
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'average_order_value': average_order_value,
        'top_selling_items': top_selling_items,
        'peak_times': peak_times
    })

if __name__ == '__main__':
    app.run(debug=True)
