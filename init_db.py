from app import app, db
from models import User, Admin, Store, Item, DeliveryStaff,Order, OrderItem 
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def init_database():
    """Initialize database with sample data for testing"""
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        user1 = User(
            username='student1', 
            email='student1@cuhk.edu.cn', 
            phone='12345678901', 
            address='Dorm A 101'
        )
        user1.set_password('password123')
        
        user2 = User(
            username='student2', 
            email='student2@cuhk.edu.cn', 
            phone='12345678902', 
            address='Dorm B 202'
        )
        user2.set_password('password123')
        
        # Create sample admin
        print("Creating admin account...")
        admin1 = Admin(
            username='admin1', 
            email='admin1@cuhk.edu.cn'
        )
        admin1.set_password('admin123')
        
        # Create sample stores
        print("Creating sample stores...")
        store1 = Store(
            store_name='学二食堂', 
            description='Traditional Chinese Cuisine', 
            address='Central Campus', 
            phone='111-1111', 
            is_active=True
        )
        
        store2 = Store(
            store_name='快乐食间', 
            description='Fast Food and Snacks', 
            address='East Campus', 
            phone='222-2222', 
            is_active=True
        )
        
        store3 = Store(
            store_name='星巴克', 
            description='Coffee and Beverages', 
            address='West Campus', 
            phone='333-3333', 
            is_active=True
        )
        
        # Create sample items for store1
        print("Creating menu items...")
        item1 = Item(
            store=store1, 
            item_name='Kung Pao Chicken', 
            description='Spicy stir-fried chicken with peanuts', 
            price=25.0, 
            category='Main Course'
        )
        
        item2 = Item(
            store=store1, 
            item_name='Mapo Tofu', 
            description='Spicy tofu with minced meat', 
            price=20.0, 
            category='Main Course'
        )
        
        item3 = Item(
            store=store1, 
            item_name='Fried Rice', 
            description='Rice stir-fried with vegetables and egg', 
            price=15.0, 
            category='Staple'
        )
        
        # Create sample items for store2
        item4 = Item(
            store=store2, 
            item_name='Cheeseburger', 
            description='Beef patty with cheese and vegetables', 
            price=18.0, 
            category='Fast Food'
        )
        
        item5 = Item(
            store=store2, 
            item_name='French Fries', 
            description='Crispy fried potatoes', 
            price=10.0, 
            category='Snack'
        )
        
        item6 = Item(
            store=store2, 
            item_name='Cola', 
            description='Carbonated soft drink', 
            price=5.0, 
            category='Beverage'
        )
        
        # Create sample items for store3
        item7 = Item(
            store=store3, 
            item_name='Latte', 
            description='Coffee with steamed milk', 
            price=30.0, 
            category='Coffee'
        )
        
        item8 = Item(
            store=store3, 
            item_name='Cappuccino', 
            description='Espresso with frothy milk', 
            price=32.0, 
            category='Coffee'
        )
        
        item9 = Item(
            store=store3, 
            item_name='Green Tea', 
            description='Traditional Chinese green tea', 
            price=20.0, 
            category='Tea'
        )
        
        # Create sample delivery staff
        print("Creating delivery staff...")
        staff1 = DeliveryStaff(
            name='John Doe', 
            phone='444-4444', 
            is_available=True
        )
        
        staff2 = DeliveryStaff(
            name='Jane Smith', 
            phone='555-5555', 
            is_available=True
        )
        
        # Add all to session and commit
        print("Committing data to database...")
        db.session.add_all([
            user1, user2, admin1, 
            store1, store2, store3, 
            item1, item2, item3, item4, item5, item6, item7, item8, item9,
            staff1, staff2
        ])
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nSample Login Credentials:")
        print("User: student1 / password123")
        print("Admin: admin1 / admin123")

        print("Adding more sample items...")
        item10 = Item(
            store=store1, 
            item_name='Sweet and Sour Pork', 
            description='Crispy pork with sweet and sour sauce', 
            price=28.0, 
            category='Main Course'
        )
        
        item11 = Item(
            store=store2, 
            item_name='Chicken Wings', 
            description='Crispy fried chicken wings', 
            price=15.0, 
            category='Snack'
        )
        
        item12 = Item(
            store=store3, 
            item_name='Americano', 
            description='Black coffee', 
            price=25.0, 
            category='Coffee'
        )
        
        # Add more delivery staff
        staff3 = DeliveryStaff(
            name='Mike Chen', 
            phone='666-6666', 
            is_available=True
        )
        
        # Add to session and commit
        print("Committing additional data to database...")
        db.session.add_all([item10, item11, item12, staff3])
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nSample Login Credentials:")
        print("User: student1 / password123")
        print("Admin: admin1 / admin123")
        print("\nSample Store IDs:")
        print("学二食堂: 1, 快乐食间: 2, 星巴克: 3")
        print("Creating sample orders with different statuses...")
        
        user1 = User.query.filter_by(username='student1').first()
        store1 = Store.query.filter_by(store_name='学二食堂').first()
        store2 = Store.query.filter_by(store_name='快乐食间').first()
        
        order1 = Order(
            user=user1,
            store=store1,
            total_amount=45.0,
            status='ready',
            delivery_address='Dorm A 101'
        )
        
        order2 = Order(
            user=user1,
            store=store2,
            total_amount=28.0,
            status='preparing', 
            delivery_address='Dorm A 101'
        )
        
        order_item1 = OrderItem(
            order=order1,
            item=item1,  # Kung Pao Chicken
            quantity=1,
            unit_price=25.0
        )
        
        order_item2 = OrderItem(
            order=order1,
            item=item3,  # Fried Rice
            quantity=1,
            unit_price=15.0
        )
        
        order_item3 = OrderItem(
            order=order2,
            item=item4,  # Cheeseburger
            quantity=1,
            unit_price=18.0
        )
        
        order_item4 = OrderItem(
            order=order2,
            item=item6,  # Cola
            quantity=2,
            unit_price=5.0
        )
        
        db.session.add_all([order1, order2, order_item1, order_item2, order_item3, order_item4])
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nSample Login Credentials:")
        print("User: student1 / password123")
        print("Admin: admin1 / admin123")
        print("\nSample Order IDs:")
        print("Ready for delivery: Order ID 1")
        print("Preparing: Order ID 2")

if __name__ == '__main__':
    init_database()