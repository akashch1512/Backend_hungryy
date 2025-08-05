from app import app
from models import db, MenuItem

# Create a list of 20 new menu items
new_items = [
    # --- Main Courses (Veg & Non-Veg) ---
    MenuItem(
        name='Chicken Tikka Masala',
        description='Tender pieces of grilled chicken simmered in a creamy tomato-based sauce.',
        price=280.0,
        image_url='https://i.ibb.co/68vM2bB/1000027116.jpg',
        category='Main Course',
        is_veg=False,
        is_available=True
    ),
    MenuItem(
        name='Matar Paneer',
        description='Cottage cheese and green peas in a rich and spicy tomato-based gravy.',
        price=190.0,
        image_url='https://i.ibb.co/cSGMvvTy/1000027112.jpg',
        category='Main Course',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Fish Curry',
        description='Spicy fish cooked in a tangy and aromatic coconut milk-based curry.',
        price=320.0,
        image_url='https://i.ibb.co/3sS7LqG/1000027113.jpg',
        category='Main Course',
        is_veg=False,
        is_available=True
    ),
    MenuItem(
        name='Aloo Gobi',
        description='A dry curry made with potatoes and cauliflower florets, spiced with turmeric and cumin.',
        price=150.0,
        image_url='https://i.ibb.co/4rL6FvR/1000027114.jpg',
        category='Main Course',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Kadai Paneer',
        description='Paneer stir-fried with bell peppers, onions, and kadai spices.',
        price=210.0,
        image_url='https://i.ibb.co/P4W1fVd/1000027115.jpg',
        category='Main Course',
        is_veg=True,
        is_available=True
    ),

    # --- Appetizers ---
    MenuItem(
        name='Samosa',
        description='Crispy pastry filled with spiced potatoes and peas, served with chutney.',
        price=50.0,
        image_url='https://i.ibb.co/68vM2bB/1000027116.jpg',
        category='Appetizers',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Chicken Seekh Kebab',
        description='Minced chicken skewers, marinated in spices and grilled to perfection.',
        price=220.0,
        image_url='https://i.ibb.co/cSGMvvTy/1000027112.jpg',
        category='Appetizers',
        is_veg=False,
        is_available=True
    ),
    MenuItem(
        name='Onion Bhaji',
        description='Deep-fried fritters made with sliced onions and gram flour.',
        price=70.0,
        image_url='https://i.ibb.co/3sS7LqG/1000027113.jpg',
        category='Appetizers',
        is_veg=True,
        is_available=True
    ),

    # --- Breads & Rice ---
    MenuItem(
        name='Garlic Naan',
        description='Soft naan bread topped with fresh garlic and cilantro.',
        price=45.0,
        image_url='https://i.ibb.co/4rL6FvR/1000027114.jpg',
        category='Bread',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Jeera Rice',
        description='Basmati rice tempered with roasted cumin seeds.',
        price=90.0,
        image_url='https://i.ibb.co/P4W1fVd/1000027115.jpg',
        category='Rice',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Tandoori Roti',
        description='Whole wheat flatbread cooked in a tandoor.',
        price=30.0,
        image_url='https://i.ibb.co/68vM2bB/1000027116.jpg',
        category='Bread',
        is_veg=True,
        is_available=True
    ),

    # --- Desserts ---
    MenuItem(
        name='Rasgulla',
        description='Spongy cottage cheese balls soaked in a light sugar syrup.',
        price=60.0,
        image_url='https://i.ibb.co/cSGMvvTy/1000027112.jpg',
        category='Desserts',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Gajar Halwa',
        description='A rich dessert made from grated carrots, milk, and sugar.',
        price=100.0,
        image_url='https://i.ibb.co/3sS7LqG/1000027113.jpg',
        category='Desserts',
        is_veg=True,
        is_available=True
    ),

    # --- Beverages ---
    MenuItem(
        name='Mango Lassi',
        description='A creamy and refreshing drink made with yogurt and ripe mango pulp.',
        price=80.0,
        image_url='https://i.ibb.co/4rL6FvR/1000027114.jpg',
        category='Beverages',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Masala Chai',
        description='Spiced tea brewed with a blend of aromatic herbs and spices.',
        price=40.0,
        image_url='https://i.ibb.co/P4W1fVd/1000027115.jpg',
        category='Beverages',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Fresh Lime Soda',
        description='A zesty and refreshing soda made with fresh lime juice, sugar, and soda water.',
        price=50.0,
        image_url='https://i.ibb.co/68vM2bB/1000027116.jpg',
        category='Beverages',
        is_veg=True,
        is_available=True
    ),
    
    # --- Additional Items ---
    MenuItem(
        name='Mutton Rogan Josh',
        description='A rich Kashmiri curry made with slow-cooked lamb and aromatic spices.',
        price=350.0,
        image_url='https://i.ibb.co/cSGMvvTy/1000027112.jpg',
        category='Main Course',
        is_veg=False,
        is_available=True
    ),
    MenuItem(
        name='Vegetable Biryani',
        description='Fragrant basmati rice cooked with mixed vegetables and whole spices.',
        price=180.0,
        image_url='https://i.ibb.co/3sS7LqG/1000027113.jpg',
        category='Main Course',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Papad',
        description='Thin, crispy lentil wafers, often served as an accompaniment.',
        price=20.0,
        image_url='https://i.ibb.co/4rL6FvR/1000027114.jpg',
        category='Appetizers',
        is_veg=True,
        is_available=True
    ),
    MenuItem(
        name='Kheer',
        description='A traditional rice pudding made with milk, rice, and sugar, garnished with nuts.',
        price=90.0,
        image_url='https://i.ibb.co/P4W1fVd/1000027115.jpg',
        category='Desserts',
        is_veg=True,
        is_available=True
    )
]

# Push app context and insert all new items
with app.app_context():
    db.session.add_all(new_items)
    db.session.commit()
    print("✅ All 20 new products have been added successfully!")

    # Optional: Print out the details of the added products
    for item in new_items:
        print(f"Product '{item.name}' added with ID: {item.id}")