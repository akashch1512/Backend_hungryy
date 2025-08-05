from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50), nullable=False)
    is_veg = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category': self.category,
            'is_veg': self.is_veg,
            'is_available': self.is_available
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100))
    delivery_address = db.Column(db.Text)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending Confirmation')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    payment = db.relationship('Payment', uselist=False, backref='order')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'delivery_address': self.delivery_address,
            'total_price': self.total_price,
            'status': self.status,
            'order_date': self.order_date.isoformat(),
            'order_items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    menu_item = db.relationship('MenuItem')

    def to_dict(self):
        return {
            'menu_item_name': self.menu_item.name,
            'quantity': self.quantity,
            'price': self.price
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Confirmed')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'booking_date': self.booking_date.isoformat(),
            'booking_time': self.booking_time.isoformat(),
            'number_of_people': self.number_of_people,
            'status': self.status
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # 'Razorpay' or 'Cash on Delivery'
    razorpay_payment_id = db.Column(db.String(100))
    razorpay_order_id = db.Column(db.String(100))
    razorpay_signature = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending') # 'Pending', 'Success', 'Failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_method': self.payment_method,
            'razorpay_payment_id': self.razorpay_payment_id,
            'amount': self.amount,
            'status': self.status,
            'payment_date': self.payment_date.isoformat()
        }
