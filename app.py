from flask import Flask, request, jsonify
from config import Config
from models import db, bcrypt, User, Admin, Store, Item, CartItem, DeliveryStaff, Order, OrderItem
from datetime import datetime, timedelta
import logging

def create_app():
    """Application factory function to create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    return app

# Create Flask application
app = create_app()

# =============================================================================
# ADMIN STORE MANAGEMENT
# =============================================================================

@app.route('/api/admin/stores', methods=['POST'])
def add_store():
    """Add a new store (admin only)"""
    try:
        data = request.get_json()
        
        store = Store(
            store_name=data.get('store_name'),
            description=data.get('description'),
            address=data.get('address'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(store)
        db.session.commit()
        
        return jsonify({
            'message': 'Store added successfully',
            'store_id': store.store_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/stores/<int:store_id>', methods=['PUT'])
def update_store(store_id):
    """Update store information (admin only)"""
    try:
        data = request.get_json()
        store = Store.query.get(store_id)
        
        if not store:
            return jsonify({'message': 'Store not found'}), 404
        
        if 'store_name' in data:
            store.store_name = data['store_name']
        if 'description' in data:
            store.description = data['description']
        if 'address' in data:
            store.address = data['address']
        if 'phone' in data:
            store.phone = data['phone']
        if 'is_active' in data:
            store.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({'message': 'Store updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/stores/<int:store_id>', methods=['DELETE'])
def delete_store(store_id):
    """Delete a store (admin only)"""
    try:
        store = Store.query.get(store_id)
        
        if not store:
            return jsonify({'message': 'Store not found'}), 404
        
        # Check if store has active orders
        active_orders = Order.query.filter_by(store_id=store_id).filter(
            Order.status.in_(['pending', 'confirmed', 'preparing', 'ready', 'assigned', 'delivering'])
        ).first()
        
        if active_orders:
            return jsonify({'message': 'Cannot delete store with active orders'}), 400
        
        # Deactivate instead of delete to preserve order history
        store.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Store deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    
# =============================================================================
# ADMIN DELIVERY STAFF MANAGEMENT
# =============================================================================

@app.route('/api/admin/delivery-staff', methods=['POST'])
def add_delivery_staff():
    """Add new delivery staff (admin only)"""
    try:
        data = request.get_json()
        
        staff = DeliveryStaff(
            name=data.get('name'),
            phone=data.get('phone'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(staff)
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery staff added successfully',
            'staff_id': staff.staff_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/delivery-staff/<int:staff_id>', methods=['DELETE'])
def delete_delivery_staff(staff_id):
    """Delete delivery staff (admin only)"""
    try:
        staff = DeliveryStaff.query.get(staff_id)
        
        if not staff:
            return jsonify({'message': 'Delivery staff not found'}), 404
        
        # Check if staff has active deliveries
        active_orders = Order.query.filter_by(delivery_staff_id=staff_id).filter(
            Order.status.in_(['assigned', 'delivering'])
        ).first()
        
        if active_orders:
            return jsonify({'message': 'Cannot delete staff with active deliveries'}), 400
        
        db.session.delete(staff)
        db.session.commit()
        
        return jsonify({'message': 'Delivery staff deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    
# =============================================================================
# ADMIN ORDER MANAGEMENT
# =============================================================================

@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders():
    """Get all orders (admin only)"""
    try:
        orders = Order.query.order_by(Order.order_time.desc()).all()
        order_list = []
        
        for order in orders:
            store = Store.query.get(order.store_id)
            user = User.query.get(order.user_id)
            delivery_staff = DeliveryStaff.query.get(order.delivery_staff_id) if order.delivery_staff_id else None
            
            order_list.append({
                'order_id': order.order_id,
                'user_name': user.username if user else 'Unknown',
                'store_name': store.store_name if store else 'Unknown Store',
                'delivery_staff': delivery_staff.name if delivery_staff else 'Not assigned',
                'total_amount': order.total_amount,
                'status': order.status,
                'order_time': order.order_time.isoformat(),
                'delivery_address': order.delivery_address
            })
        
        return jsonify({'orders': order_list}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>/assign', methods=['PUT'])
def assign_delivery_staff(order_id):
    """Assign delivery staff to an order (admin only)"""
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if staff exists and is available
        staff = DeliveryStaff.query.filter_by(staff_id=staff_id, is_available=True).first()
        if not staff:
            return jsonify({'message': 'Delivery staff not found or unavailable'}), 404
        
        # Only assign orders that are ready for delivery
        if order.status not in ['ready']:
            return jsonify({'message': 'Order is not ready for delivery'}), 400
        
        order.delivery_staff_id = staff_id
        order.status = 'assigned'
        db.session.commit()
        
        return jsonify({'message': 'Delivery staff assigned successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    
# =============================================================================
# ADDITIONAL ADMIN ENDPOINTS
# =============================================================================

@app.route('/api/admin/delivery-staff', methods=['GET'])
def get_all_delivery_staff():
    """Get all delivery staff (admin only)"""
    try:
        staff_list = DeliveryStaff.query.all()
        staff_data = []
        
        for staff in staff_list:
            staff_data.append({
                'staff_id': staff.staff_id,
                'name': staff.name,
                'phone': staff.phone,
                'is_available': staff.is_available,
                'created_at': staff.created_at.isoformat()
            })
        
        return jsonify({'delivery_staff': staff_data}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/stores/all', methods=['GET'])
def get_all_stores_admin():
    """Get all stores including inactive ones (admin only)"""
    try:
        stores = Store.query.all()
        store_list = []
        
        for store in stores:
            store_list.append({
                'store_id': store.store_id,
                'store_name': store.store_name,
                'description': store.description,
                'address': store.address,
                'phone': store.phone,
                'is_active': store.is_active,
                'created_at': store.created_at.isoformat()
            })
        
        return jsonify({'stores': store_list}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """Get detailed information about a specific order (admin only)"""

# =============================================================================
# ORDER STATUS MANAGEMENT
# =============================================================================

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status (admin only)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # verify the status is valid
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'assigned', 'delivering', 'delivered', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'message': 'Invalid status'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({'message': 'Order status updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/admin/orders/ready', methods=['GET'])
def get_ready_orders():
    """Get all orders with status 'ready' for delivery assignment"""
    try:
        ready_orders = Order.query.filter_by(status='ready').all()
        order_list = []
        
        for order in ready_orders:
            store = Store.query.get(order.store_id)
            user = User.query.get(order.user_id)
            
            order_list.append({
                'order_id': order.order_id,
                'user_name': user.username if user else 'Unknown',
                'store_name': store.store_name if store else 'Unknown Store',
                'total_amount': order.total_amount,
                'order_time': order.order_time.isoformat(),
                'delivery_address': order.delivery_address
            })
        
        return jsonify({'orders': order_list}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

# =============================================================================
# USER AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user account"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.user_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and user.check_password(data.get('password')):
            return jsonify({
                'message': 'Login successful',
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email
            }), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        admin = Admin.query.filter_by(username=data.get('username')).first()
        
        if admin and admin.check_password(data.get('password')):
            return jsonify({
                'message': 'Admin login successful',
                'admin_id': admin.admin_id,
                'username': admin.username
            }), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# =============================================================================
# STORE AND ITEM ENDPOINTS
# =============================================================================

@app.route('/api/stores', methods=['GET'])
def get_stores():
    """Get all active stores"""
    try:
        stores = Store.query.filter_by(is_active=True).all()
        store_list = []
        for store in stores:
            store_list.append({
                'store_id': store.store_id,
                'store_name': store.store_name,
                'description': store.description,
                'address': store.address,
                'phone': store.phone
            })
        return jsonify({'stores': store_list}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/stores/<int:store_id>/items', methods=['GET'])
def get_store_items(store_id):
    """Get all available items for a specific store"""
    try:
        items = Item.query.filter_by(store_id=store_id, is_available=True).all()
        item_list = []
        for item in items:
            item_list.append({
                'item_id': item.item_id,
                'item_name': item.item_name,
                'description': item.description,
                'price': item.price,
                'category': item.category
            })
        return jsonify({'items': item_list}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# =============================================================================
# CART MANAGEMENT ENDPOINTS
# =============================================================================

@app.route('/api/users/<int:user_id>/cart', methods=['GET'])
def get_cart(user_id):
    """Get user's shopping cart items"""
    try:
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        cart_list = []
        total = 0
        
        for cart_item in cart_items:
            item = Item.query.get(cart_item.item_id)
            if item and item.is_available:
                item_total = item.price * cart_item.quantity
                total += item_total
                
                cart_list.append({
                    'cart_item_id': cart_item.cart_item_id,
                    'item_id': item.item_id,
                    'item_name': item.item_name,
                    'price': item.price,
                    'quantity': cart_item.quantity,
                    'item_total': item_total
                })
        
        return jsonify({
            'cart_items': cart_list,
            'total_amount': total
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<int:user_id>/cart', methods=['POST'])
def add_to_cart(user_id):
    """Add item to user's shopping cart"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        # Check if item exists and is available
        item = Item.query.filter_by(item_id=item_id, is_available=True).first()
        if not item:
            return jsonify({'message': 'Item not found or unavailable'}), 404
        
        # Check if item is already in cart
        existing_cart_item = CartItem.query.filter_by(
            user_id=user_id, 
            item_id=item_id
        ).first()
        
        if existing_cart_item:
            # Update quantity if item already in cart
            existing_cart_item.quantity += quantity
        else:
            # Add new item to cart
            cart_item = CartItem(
                user_id=user_id,
                item_id=item_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Item added to cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<int:user_id>/cart/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(user_id, cart_item_id):
    """Remove item from user's shopping cart"""
    try:
        cart_item = CartItem.query.filter_by(
            cart_item_id=cart_item_id,
            user_id=user_id
        ).first()
        
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# =============================================================================
# ORDER MANAGEMENT ENDPOINTS (Basic implementation)
# =============================================================================

@app.route('/api/users/<int:user_id>/orders', methods=['POST'])
def create_order(user_id):
    """Create a new order from user's cart"""
    try:
        data = request.get_json()
        delivery_address = data.get('delivery_address')
        
        if not delivery_address:
            return jsonify({'message': 'Delivery address is required'}), 400
        
        # Get user's cart items
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400
        
        # Calculate total amount and group by store
        store_totals = {}
        store_items = {}
        
        for cart_item in cart_items:
            item = Item.query.get(cart_item.item_id)
            if item and item.is_available:
                store_id = item.store_id
                if store_id not in store_totals:
                    store_totals[store_id] = 0
                    store_items[store_id] = []
                
                item_total = item.price * cart_item.quantity
                store_totals[store_id] += item_total
                store_items[store_id].append({
                    'item': item,
                    'quantity': cart_item.quantity,
                    'unit_price': item.price
                })
        
        # Create orders for each store
        order_ids = []
        for store_id, total_amount in store_totals.items():
            order = Order(
                user_id=user_id,
                store_id=store_id,
                total_amount=total_amount,
                delivery_address=delivery_address,
                status='pending'
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add order items
            for item_data in store_items[store_id]:
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=item_data['item'].item_id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                db.session.add(order_item)
            
            order_ids.append(order.order_id)
        
        # Clear user's cart
        CartItem.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order_ids': order_ids
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a specific user"""
    try:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_time.desc()).all()
        order_list = []
        
        for order in orders:
            store = Store.query.get(order.store_id)
            order_list.append({
                'order_id': order.order_id,
                'store_name': store.store_name if store else 'Unknown Store',
                'total_amount': order.total_amount,
                'status': order.status,
                'order_time': order.order_time.isoformat(),
                'delivery_address': order.delivery_address
            })
        
        return jsonify({'orders': order_list}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'CUHK Food Ordering API'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# =============================================================================
# USER PROFILE MANAGEMENT
# =============================================================================

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile information"""
    try:
        data = request.get_json()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Update fields if provided
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.user_id != user_id:
                return jsonify({'message': 'Email already taken'}), 400
            user.email = data['email']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        if 'address' in data:
            user.address = data['address']
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    
# =============================================================================
# ORDER MANAGMENT ENDPOINTS (Advanced implementation)
# =============================================================================

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order (cancel or modify) - only for pending orders"""
    try:
        data = request.get_json()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Only allow modification for pending orders
        if order.status not in ['pending', 'confirmed']:
            return jsonify({'message': 'Cannot modify order in current status'}), 400
        
        # Cancel order
        if data.get('action') == 'cancel':
            order.status = 'cancelled'
            db.session.commit()
            return jsonify({'message': 'Order cancelled successfully'}), 200
        
        # Modify delivery address
        if 'delivery_address' in data:
            order.delivery_address = data['delivery_address']
            db.session.commit()
            return jsonify({'message': 'Order updated successfully'}), 200
        
        return jsonify({'message': 'No valid update operation specified'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/orders/<int:order_id>/confirm', methods=['PUT'])
def confirm_delivery(order_id):
    """Confirm order delivery"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Only allow confirmation for delivered orders
        if order.status != 'delivered':
            return jsonify({'message': 'Order is not yet delivered'}), 400
        
        order.status = 'completed'
        db.session.commit()
        
        return jsonify({'message': 'Order confirmed as completed'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    