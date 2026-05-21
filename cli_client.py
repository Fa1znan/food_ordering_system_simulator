import requests
import json
import getpass
import sys

# API base URL
BASE_URL = 'http://localhost:5000/api'

class FoodOrderingCLI:
    def __init__(self):
        self.current_user = None
        self.token = None
    def make_admin_request(self, method, endpoint, data=None):
        try:
            url = f'{BASE_URL}{endpoint}'
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers={'Content-Type': 'application/json'}, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=10)
            else:
                return None, "Invalid method"
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json(), None
            else:
                try:
                    error_data = response.json()
                    return None, error_data.get('message', f"Error {response.status_code}")
                except json.JSONDecodeError:
                    return None, f"Server error: {response.status_code}"
                    
        except requests.exceptions.ConnectionError:
            return None, "Cannot connect to server"
        except requests.exceptions.Timeout:
            return None, "Request timed out"
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"
        
    def display_menu(self):
        """Display main menu based on user type"""
        if self.current_user is None:
            self.guest_menu()
        else:
            # Check if user is admin
            if hasattr(self.current_user, 'get') and self.current_user.get('is_admin'):
                self.admin_menu()
            else:
                self.user_menu()
    
    def guest_menu(self):
        """Display menu for guests (not logged in)"""
        print("\n" + "="*50)
        print("        CUHK Food Ordering System")
        print("="*50)
        print("1. User Login")
        print("2. User Registration")
        print("3. Admin Login")
        print("4. Exit")
        print("-"*50)
        
        choice = input("Please select an option: ").strip()
        
        if choice == '1':
            self.user_login()
        elif choice == '2':
            self.user_register()
        elif choice == '3':
            self.admin_login()
        elif choice == '4':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please try again.")
            input("Press Enter to continue...")
    
    def user_menu(self):
        """Display menu for regular users"""
        print(f"\n" + "="*50)
        print(f"    Welcome, {self.current_user['username']}!")
        print("="*50)
        print("1. Browse Stores")
        print("2. View Store Menu")
        print("3. View My Cart")
        print("4. Add Item to Cart")
        print("5. Remove Item from Cart")
        print("6. Place Order")
        print("7. View My Orders")
        print("8. Logout")
        print("-"*50)
        
        choice = input("Please select an option: ").strip()
        
        if choice == '1':
            self.list_stores()
        elif choice == '2':
            store_id = input("Enter Store ID: ").strip()
            if store_id.isdigit():
                self.list_store_items(int(store_id))
            else:
                print("Invalid Store ID")
                input("Press Enter to continue...")
        elif choice == '3':
            self.view_cart()
        elif choice == '4':
            self.add_to_cart()
        elif choice == '5':
            self.remove_from_cart()
        elif choice == '6':
            self.place_order()
        elif choice == '7':
            self.view_orders()
        elif choice == '8':
            self.logout()
        else:
            print("Invalid selection. Please try again.")
            input("Press Enter to continue...")
    
    def admin_menu(self):
        """Display menu for administrators"""
        print(f"\n" + "="*50)
        print(f"    Admin Panel - {self.current_user['username']}")
        print("="*50)
        print("1. View All Orders")
        print("2. Manage Stores")
        print("3. Manage Delivery Staff") 
        print("4. Assign Delivery Staff")
        print("5. Manage Order Status")
        print("6. Logout")
        print("-"*50)
        
        choice = input("Please select an option: ").strip()
        
        if choice == '1':
            self.view_all_orders()
        elif choice == '2':
            self.manage_stores()
        elif choice == '3':
            self.manage_delivery_staff()
        elif choice == '4':
            self.assign_delivery_staff()
        elif choice == '5':
            self.manage_order_status()
        elif choice == '6':
            self.logout()
        else:
            print("Invalid selection. Please try again.")
            input("Press Enter to continue...")

    def user_login(self):
        """Handle user login"""
        print("\n--- User Login ---")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        response = requests.post(f'{BASE_URL}/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            self.current_user = response.json()
            print(f"Login successful! Welcome {self.current_user['username']}")
        else:
            print(f"Login failed: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def admin_login(self):
        """Handle admin login"""
        print("\n--- Admin Login ---")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        response = requests.post(f'{BASE_URL}/admin/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            self.current_user = response.json()
            self.current_user['is_admin'] = True
            print(f"Admin login successful! Welcome {self.current_user['username']}")
        else:
            print(f"Login failed: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def user_register(self):
        """Handle user registration"""
        print("\n--- User Registration ---")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        address = input("Address: ").strip()
        password = getpass.getpass("Password: ").strip()
        confirm_password = getpass.getpass("Confirm Password: ").strip()
        
        if password != confirm_password:
            print("Passwords do not match!")
            input("Press Enter to continue...")
            return
        
        response = requests.post(f'{BASE_URL}/register', json={
            'username': username,
            'email': email,
            'phone': phone,
            'address': address,
            'password': password
        })
        
        if response.status_code == 201:
            print("Registration successful! Please login.")
        else:
            print(f"Registration failed: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def list_stores(self):
        """List all active stores"""
        print("\n--- Available Stores ---")
        response = requests.get(f'{BASE_URL}/stores')
        
        if response.status_code == 200:
            stores = response.json().get('stores', [])
            if stores:
                for store in stores:
                    print(f"\nStore ID: {store['store_id']}")
                    print(f"Name: {store['store_name']}")
                    print(f"Description: {store['description']}")
                    print(f"Address: {store['address']}")
                    print(f"Phone: {store['phone']}")
                    print("-" * 30)
            else:
                print("No stores found.")
        else:
            print(f"Failed to fetch stores: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def list_store_items(self, store_id):
        """List all items for a specific store"""
        print(f"\n--- Store Menu ---")
        response = requests.get(f'{BASE_URL}/stores/{store_id}/items')
        
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                for item in items:
                    print(f"\nItem ID: {item['item_id']}")
                    print(f"Name: {item['item_name']}")
                    print(f"Description: {item['description']}")
                    print(f"Price: ${item['price']:.2f}")
                    print(f"Category: {item['category']}")
                    print("-" * 30)
            else:
                print("No items found for this store.")
        else:
            print(f"Failed to fetch menu: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def view_cart(self):
        """View user's shopping cart"""
        user_id = self.current_user['user_id']
        print(f"\n--- Shopping Cart ---")
        response = requests.get(f'{BASE_URL}/users/{user_id}/cart')
        
        if response.status_code == 200:
            cart_data = response.json()
            cart_items = cart_data.get('cart_items', [])
            total = cart_data.get('total_amount', 0)
            
            if cart_items:
                for item in cart_items:
                    print(f"\nItem: {item['item_name']}")
                    print(f"Quantity: {item['quantity']}")
                    print(f"Price: ${item['price']:.2f} each")
                    print(f"Subtotal: ${item['item_total']:.2f}")
                    print("-" * 30)
                
                print(f"\nTotal: ${total:.2f}")
            else:
                print("Your cart is empty.")
        else:
            print(f"Failed to fetch cart: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def add_to_cart(self):
        """Add item to user's shopping cart"""
        user_id = self.current_user['user_id']
        print("\n--- Add to Cart ---")
        
        item_id = input("Enter Item ID: ").strip()
        quantity = input("Enter Quantity (default 1): ").strip()
        
        if not quantity:
            quantity = 1
        else:
            try:
                quantity = int(quantity)
            except ValueError:
                print("Invalid quantity!")
                input("Press Enter to continue...")
                return
        
        response = requests.post(f'{BASE_URL}/users/{user_id}/cart', json={
            'item_id': int(item_id),
            'quantity': quantity
        })
        
        if response.status_code == 200:
            print("Item added to cart successfully!")
        else:
            print(f"Failed to add item: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def remove_from_cart(self):
        """Remove item from user's shopping cart"""
        user_id = self.current_user['user_id']
        print("\n--- Remove from Cart ---")
        
        # First show the current cart
        cart_response = requests.get(f'{BASE_URL}/users/{user_id}/cart')
        if cart_response.status_code != 200:
            print("Failed to fetch cart")
            input("Press Enter to continue...")
            return
        
        cart_items = cart_response.json().get('cart_items', [])
        if not cart_items:
            print("Your cart is empty.")
            input("Press Enter to continue...")
            return
        
        print("Your Cart Items:")
        for item in cart_items:
            print(f"Cart Item ID: {item['cart_item_id']} - {item['item_name']} (Qty: {item['quantity']})")
        
        cart_item_id = input("\nEnter Cart Item ID to remove: ").strip()
        
        if not cart_item_id.isdigit():
            print("Invalid Cart Item ID!")
            input("Press Enter to continue...")
            return
        
        response = requests.delete(f'{BASE_URL}/users/{user_id}/cart/{int(cart_item_id)}')
        
        if response.status_code == 200:
            print("Item removed from cart successfully!")
        else:
            print(f"Failed to remove item: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def place_order(self):
        """Place order from user's cart"""
        user_id = self.current_user['user_id']
        print("\n--- Place Order ---")
        
        # Show current cart
        cart_response = requests.get(f'{BASE_URL}/users/{user_id}/cart')
        if cart_response.status_code != 200:
            print("Failed to fetch cart")
            input("Press Enter to continue...")
            return
        
        cart_data = cart_response.json()
        cart_items = cart_data.get('cart_items', [])
        total = cart_data.get('total_amount', 0)
        
        if not cart_items:
            print("Your cart is empty. Add items before placing an order.")
            input("Press Enter to continue...")
            return
        
        print("Order Summary:")
        for item in cart_items:
            print(f"- {item['item_name']} x{item['quantity']}: ${item['item_total']:.2f}")
        print(f"Total: ${total:.2f}")
        
        delivery_address = input("\nEnter delivery address: ").strip()
        if not delivery_address:
            print("Delivery address is required!")
            input("Press Enter to continue...")
            return
        
        confirm = input("\nConfirm order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            input("Press Enter to continue...")
            return
        
        response = requests.post(f'{BASE_URL}/users/{user_id}/orders', json={
            'delivery_address': delivery_address
        })
        
        if response.status_code == 201:
            order_data = response.json()
            print(f"Order placed successfully!")
            print(f"Order IDs: {order_data['order_ids']}")
        else:
            print(f"Failed to place order: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def view_orders(self):
        """View user's orders"""
        user_id = self.current_user['user_id']
        print(f"\n--- My Orders ---")
        response = requests.get(f'{BASE_URL}/users/{user_id}/orders')
        
        if response.status_code == 200:
            orders = response.json().get('orders', [])
            if orders:
                for order in orders:
                    print(f"\nOrder ID: {order['order_id']}")
                    print(f"Store: {order['store_name']}")
                    print(f"Total: ${order['total_amount']:.2f}")
                    print(f"Status: {order['status']}")
                    print(f"Order Time: {order['order_time']}")
                    print(f"Address: {order['delivery_address']}")
                    print("-" * 40)
            else:
                print("No orders found.")
        else:
            print(f"Failed to fetch orders: {response.json().get('message')}")
        
        input("Press Enter to continue...")
    
    def view_all_orders(self):
        """View all orders (admin only)"""
        print("\n--- All Orders ---")
        print("This feature will be implemented in the next phase.")
        input("Press Enter to continue...")
    
    def view_profile(self):
        """View user profile"""
        user_id = self.current_user['user_id']
        print(f"\n--- My Profile ---")
        response = requests.get(f'{BASE_URL}/users/{user_id}')
        
        if response.status_code == 200:
            profile = response.json()
            print(f"Username: {profile['username']}")
            print(f"Email: {profile['email']}")
            print(f"Phone: {profile['phone']}")
            print(f"Address: {profile['address']}")
            print(f"Member since: {profile['created_at'][:10]}")
        else:
            print(f"Failed to fetch profile: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def update_profile(self):
        """Update user profile"""
        user_id = self.current_user['user_id']
        print(f"\n--- Update Profile ---")
        
        # First get current profile
        response = requests.get(f'{BASE_URL}/users/{user_id}')
        if response.status_code != 200:
            print("Failed to fetch current profile")
            input("Press Enter to continue...")
            return
        
        current_profile = response.json()
        
        print("Leave field blank to keep current value:")
        new_email = input(f"Email [{current_profile['email']}]: ").strip()
        new_phone = input(f"Phone [{current_profile['phone']}]: ").strip()
        new_address = input(f"Address [{current_profile['address']}]: ").strip()
        
        update_data = {}
        if new_email:
            update_data['email'] = new_email
        if new_phone:
            update_data['phone'] = new_phone
        if new_address:
            update_data['address'] = new_address
        
        if not update_data:
            print("No changes made.")
            input("Press Enter to continue...")
            return
        
        response = requests.put(f'{BASE_URL}/users/{user_id}', json=update_data)
        
        if response.status_code == 200:
            print("Profile updated successfully!")
        else:
            print(f"Failed to update profile: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def update_order(self):
        """Update or cancel an order"""
        user_id = self.current_user['user_id']
        print(f"\n--- Update Order ---")
        
        # First show user's orders
        orders_response = requests.get(f'{BASE_URL}/users/{user_id}/orders')
        if orders_response.status_code != 200:
            print("Failed to fetch orders")
            input("Press Enter to continue...")
            return
        
        orders = orders_response.json().get('orders', [])
        if not orders:
            print("No orders found.")
            input("Press Enter to continue...")
            return
        
        print("Your Orders:")
        for order in orders:
            if order['status'] in ['pending', 'confirmed']:
                print(f"Order ID: {order['order_id']} - {order['store_name']} - ${order['total_amount']:.2f} - {order['status']}")
        
        order_id = input("\nEnter Order ID to update: ").strip()
        if not order_id.isdigit():
            print("Invalid Order ID!")
            input("Press Enter to continue...")
            return
        
        print("\nUpdate Options:")
        print("1. Cancel Order")
        print("2. Change Delivery Address")
        
        option = input("Select option: ").strip()
        
        if option == '1':
            response = requests.put(f'{BASE_URL}/orders/{int(order_id)}', json={'action': 'cancel'})
            if response.status_code == 200:
                print("Order cancelled successfully!")
            else:
                print(f"Failed to cancel order: {response.json().get('message')}")
        
        elif option == '2':
            new_address = input("Enter new delivery address: ").strip()
            if new_address:
                response = requests.put(f'{BASE_URL}/orders/{int(order_id)}', json={'delivery_address': new_address})
                if response.status_code == 200:
                    print("Delivery address updated successfully!")
                else:
                    print(f"Failed to update address: {response.json().get('message')}")
            else:
                print("Address cannot be empty!")
        
        else:
            print("Invalid option!")
        
        input("Press Enter to continue...")

    def confirm_delivery(self):
        """Confirm order delivery"""
        user_id = self.current_user['user_id']
        print(f"\n--- Confirm Delivery ---")
        
        # Show delivered orders
        orders_response = requests.get(f'{BASE_URL}/users/{user_id}/orders')
        if orders_response.status_code != 200:
            print("Failed to fetch orders")
            input("Press Enter to continue...")
            return
        
        orders = orders_response.json().get('orders', [])
        delivered_orders = [order for order in orders if order['status'] == 'delivered']
        
        if not delivered_orders:
            print("No delivered orders waiting for confirmation.")
            input("Press Enter to continue...")
            return
        
        print("Delivered Orders:")
        for order in delivered_orders:
            print(f"Order ID: {order['order_id']} - {order['store_name']} - ${order['total_amount']:.2f}")
        
        order_id = input("\nEnter Order ID to confirm delivery: ").strip()
        if not order_id.isdigit():
            print("Invalid Order ID!")
            input("Press Enter to continue...")
            return
        
        response = requests.put(f'{BASE_URL}/orders/{int(order_id)}/confirm')
        if response.status_code == 200:
            print("Delivery confirmed! Order marked as completed.")
        else:
            print(f"Failed to confirm delivery: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def view_all_orders(self):
        """View all orders in the system (admin only)"""
        print("\n--- All Orders ---")
        response = requests.get(f'{BASE_URL}/admin/orders')
        
        if response.status_code == 200:
            orders = response.json().get('orders', [])
            if orders:
                for order in orders:
                    print(f"\nOrder ID: {order['order_id']}")
                    print(f"Customer: {order['user_name']}")
                    print(f"Store: {order['store_name']}")
                    print(f"Delivery Staff: {order['delivery_staff']}")
                    print(f"Total: ${order['total_amount']:.2f}")
                    print(f"Status: {order['status']}")
                    print(f"Order Time: {order['order_time']}")
                    print(f"Address: {order['delivery_address']}")
                    print("-" * 40)
            else:
                print("No orders found.")
        else:
            print(f"Failed to fetch orders: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def manage_stores(self):
        """Store management submenu for admin"""
        while True:
            print("\n" + "="*50)
            print("        Store Management")
            print("="*50)
            print("1. List All Stores")
            print("2. Add New Store")
            print("3. Update Store")
            print("4. Delete Store")
            print("5. Back to Admin Menu")
            print("-"*50)
            
            choice = input("Please select an option: ").strip()
            
            if choice == '1':
                self.list_all_stores()
            elif choice == '2':
                self.add_store()
            elif choice == '3':
                self.update_store()
            elif choice == '4':
                self.delete_store()
            elif choice == '5':
                break
            else:
                print("Invalid selection. Please try again.")
                input("Press Enter to continue...")

    def list_all_stores(self):
        """List all stores including inactive ones"""
        print("\n--- All Stores ---")
        # We'll use the existing stores endpoint and handle inactive stores in the display
        response = requests.get(f'{BASE_URL}/stores')
        
        if response.status_code == 200:
            stores = response.json().get('stores', [])
            if stores:
                for store in stores:
                    status = "Active" if store.get('is_active', True) else "Inactive"
                    print(f"\nStore ID: {store['store_id']}")
                    print(f"Name: {store['store_name']}")
                    print(f"Description: {store['description']}")
                    print(f"Address: {store['address']}")
                    print(f"Phone: {store['phone']}")
                    print(f"Status: {status}")
                    print("-" * 30)
            else:
                print("No stores found.")
        else:
            print(f"Failed to fetch stores: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def add_store(self):
        """Add a new store"""
        print("\n--- Add New Store ---")
        
        store_name = input("Store Name: ").strip()
        description = input("Description: ").strip()
        address = input("Address: ").strip()
        phone = input("Phone: ").strip()
        
        if not store_name:
            print("Store name is required!")
            input("Press Enter to continue...")
            return
        
        store_data = {
            'store_name': store_name,
            'description': description,
            'address': address,
            'phone': phone
        }
        
        response = requests.post(f'{BASE_URL}/admin/stores', json=store_data)
        
        if response.status_code == 201:
            store_id = response.json().get('store_id')
            print(f"Store added successfully! Store ID: {store_id}")
        else:
            print(f"Failed to add store: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def update_store(self):
        """Update store information"""
        print("\n--- Update Store ---")
        
        # First list all stores
        self.list_all_stores()
        
        store_id = input("\nEnter Store ID to update: ").strip()
        if not store_id.isdigit():
            print("Invalid Store ID!")
            input("Press Enter to continue...")
            return
        
        # Get current store info
        response = requests.get(f'{BASE_URL}/stores')
        if response.status_code != 200:
            print("Failed to fetch stores")
            input("Press Enter to continue...")
            return
        
        stores = response.json().get('stores', [])
        current_store = None
        for store in stores:
            if store['store_id'] == int(store_id):
                current_store = store
                break
        
        if not current_store:
            print("Store not found!")
            input("Press Enter to continue...")
            return
        
        print("\nLeave field blank to keep current value:")
        new_name = input(f"Store Name [{current_store['store_name']}]: ").strip()
        new_desc = input(f"Description [{current_store['description']}]: ").strip()
        new_addr = input(f"Address [{current_store['address']}]: ").strip()
        new_phone = input(f"Phone [{current_store['phone']}]: ").strip()
        new_active = input(f"Active (y/n) [{'y' if current_store.get('is_active', True) else 'n'}]: ").strip().lower()
        
        update_data = {}
        if new_name:
            update_data['store_name'] = new_name
        if new_desc:
            update_data['description'] = new_desc
        if new_addr:
            update_data['address'] = new_addr
        if new_phone:
            update_data['phone'] = new_phone
        if new_active:
            update_data['is_active'] = (new_active == 'y')
        
        if not update_data:
            print("No changes made.")
            input("Press Enter to continue...")
            return
        
        response = requests.put(f'{BASE_URL}/admin/stores/{int(store_id)}', json=update_data)
        
        if response.status_code == 200:
            print("Store updated successfully!")
        else:
            print(f"Failed to update store: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def delete_store(self):
        """Delete (deactivate) a store"""
        print("\n--- Delete Store ---")
        
        # First list all stores
        self.list_all_stores()
        
        store_id = input("\nEnter Store ID to delete: ").strip()
        if not store_id.isdigit():
            print("Invalid Store ID!")
            input("Press Enter to continue...")
            return
        
        confirm = input("Are you sure you want to delete this store? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            input("Press Enter to continue...")
            return
        
        response = requests.delete(f'{BASE_URL}/admin/stores/{int(store_id)}')
        
        if response.status_code == 200:
            print("Store deleted successfully!")
        else:
            print(f"Failed to delete store: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def manage_delivery_staff(self):
        """Delivery staff management submenu for admin"""
        while True:
            print("\n" + "="*50)
            print("    Delivery Staff Management")
            print("="*50)
            print("1. List All Delivery Staff")
            print("2. Add New Delivery Staff")
            print("3. Delete Delivery Staff")
            print("4. Back to Admin Menu")
            print("-"*50)
            
            choice = input("Please select an option: ").strip()
            
            if choice == '1':
                self.list_delivery_staff()
            elif choice == '2':
                self.add_delivery_staff()
            elif choice == '3':
                self.delete_delivery_staff()
            elif choice == '4':
                break
            else:
                print("Invalid selection. Please try again.")
                input("Press Enter to continue...")

    def list_delivery_staff(self):
        """List all delivery staff"""
        print("\n--- Delivery Staff ---")
        response = requests.get(f'{BASE_URL}/admin/delivery-staff')
        
        if response.status_code == 200:
            staff_list = response.json().get('delivery_staff', [])
            if staff_list:
                for staff in staff_list:
                    status = "Available" if staff['is_available'] else "Unavailable"
                    print(f"\nStaff ID: {staff['staff_id']}")
                    print(f"Name: {staff['name']}")
                    print(f"Phone: {staff['phone']}")
                    print(f"Status: {status}")
                    print(f"Joined: {staff['created_at'][:10]}")
                    print("-" * 30)
            else:
                print("No delivery staff found.")
        else:
            print(f"Failed to fetch delivery staff: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def add_delivery_staff(self):
        """Add new delivery staff"""
        print("\n--- Add Delivery Staff ---")
        
        name = input("Name: ").strip()
        phone = input("Phone: ").strip()
        
        if not name:
            print("Name is required!")
            input("Press Enter to continue...")
            return
        
        staff_data = {
            'name': name,
            'phone': phone
        }
        
        response = requests.post(f'{BASE_URL}/admin/delivery-staff', json=staff_data)
        
        if response.status_code == 201:
            staff_id = response.json().get('staff_id')
            print(f"Delivery staff added successfully! Staff ID: {staff_id}")
        else:
            print(f"Failed to add delivery staff: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def delete_delivery_staff(self):
        """Delete delivery staff"""
        print("\n--- Delete Delivery Staff ---")
        
        # First list all staff
        self.list_delivery_staff()
        
        staff_id = input("\nEnter Staff ID to delete: ").strip()
        if not staff_id.isdigit():
            print("Invalid Staff ID!")
            input("Press Enter to continue...")
            return
        
        confirm = input("Are you sure you want to delete this staff member? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            input("Press Enter to continue...")
            return
        
        response = requests.delete(f'{BASE_URL}/admin/delivery-staff/{int(staff_id)}')
        
        if response.status_code == 200:
            print("Delivery staff deleted successfully!")
        else:
            print(f"Failed to delete delivery staff: {response.json().get('message')}")
        
        input("Press Enter to continue...")

    def assign_delivery_staff(self):
        """Assign delivery staff to orders"""
        print("\n--- Assign Delivery Staff ---")
        
        result, error = self.make_admin_request('GET', '/admin/orders/ready')
        if error:
            print(f"Error: {error}")
            input("Press Enter to continue...")
            return
        
        ready_orders = result.get('orders', [])
        
        if not ready_orders:
            print("No orders ready for delivery assignment.")
            input("Press Enter to continue...")
            return
        
        print("Orders Ready for Delivery Assignment:")
        for order in ready_orders:
            print(f"Order ID: {order['order_id']} - {order['store_name']} - ${order['total_amount']:.2f}")
        
        order_id = input("\nEnter Order ID to assign: ").strip()
        if not order_id.isdigit():
            print("Invalid Order ID!")
            input("Press Enter to continue...")
            return
        
        staff_result, staff_error = self.make_admin_request('GET', '/admin/delivery-staff')
        if staff_error:
            print(f"Error: {staff_error}")
            input("Press Enter to continue...")
            return
        
        staff_list = staff_result.get('delivery_staff', [])
        available_staff = [staff for staff in staff_list if staff['is_available']]
        
        if not available_staff:
            print("No available delivery staff!")
            input("Press Enter to continue...")
            return
        
        print("\nAvailable Delivery Staff:")
        for staff in available_staff:
            print(f"Staff ID: {staff['staff_id']} - {staff['name']} - {staff['phone']}")
        
        staff_id = input("\nEnter Staff ID to assign: ").strip()
        if not staff_id.isdigit():
            print("Invalid Staff ID!")
            input("Press Enter to continue...")
            return
        
        assign_data = {
            'staff_id': int(staff_id)
        }
        
        result, error = self.make_admin_request('PUT', f'/admin/orders/{int(order_id)}/assign', assign_data)
        
        if error:
            print(f"Error: {error}")
        else:
            print("Delivery staff assigned successfully!")
        
        input("Press Enter to continue...")
        
    def manage_order_status(self):
        """Order status management submenu for admin"""
        while True:
            print("\n" + "="*50)
            print("        Order Status Management")
            print("="*50)
            print("1. View All Orders with Status")
            print("2. Update Order Status")
            print("3. View Ready Orders")
            print("4. Back to Admin Menu")
            print("-"*50)
            
            choice = input("Please select an option: ").strip()
            
            if choice == '1':
                self.view_all_orders_with_status()
            elif choice == '2':
                self.update_order_status()
            elif choice == '3':
                self.view_ready_orders()
            elif choice == '4':
                break
            else:
                print("Invalid selection. Please try again.")
                input("Press Enter to continue...")

    def view_all_orders_with_status(self):
        """View all orders with detailed status information"""
        print("\n--- All Orders with Status ---")
        result, error = self.make_admin_request('GET', '/admin/orders')
        
        if error:
            print(f"Error: {error}")
        else:
            orders = result.get('orders', [])
            if orders:
                status_groups = {}
                for order in orders:
                    status = order['status']
                    if status not in status_groups:
                        status_groups[status] = []
                    status_groups[status].append(order)
                
                for status, order_list in status_groups.items():
                    print(f"\n--- {status.upper()} Orders ({len(order_list)}) ---")
                    for order in order_list:
                        print(f"Order ID: {order['order_id']} - {order['store_name']} - ${order['total_amount']:.2f}")
            else:
                print("No orders found.")
        
        input("Press Enter to continue...")

    def update_order_status(self):
        """Update the status of an order"""
        print("\n--- Update Order Status ---")
        
        result, error = self.make_admin_request('GET', '/admin/orders')
        if error:
            print(f"Error: {error}")
            input("Press Enter to continue...")
            return
        
        orders = result.get('orders', [])
        if not orders:
            print("No orders found.")
            input("Press Enter to continue...")
            return
        
        print("All Orders:")
        for order in orders:
            print(f"Order ID: {order['order_id']} - Status: {order['status']} - {order['store_name']} - ${order['total_amount']:.2f}")
        
        order_id = input("\nEnter Order ID to update: ").strip()
        if not order_id.isdigit():
            print("Invalid Order ID!")
            input("Press Enter to continue...")
            return
        
        print("\nValid Order Statuses:")
        print("pending - Order placed, waiting for confirmation")
        print("confirmed - Order confirmed by store")
        print("preparing - Store is preparing the order")
        print("ready - Order is ready for delivery")
        print("assigned - Delivery staff assigned")
        print("delivering - Order is out for delivery")
        print("delivered - Order has been delivered")
        print("completed - Customer confirmed receipt")
        print("cancelled - Order was cancelled")
        
        new_status = input("\nEnter new status: ").strip().lower()
        
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'assigned', 'delivering', 'delivered', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            print("Invalid status!")
            input("Press Enter to continue...")
            return
        
        update_data = {
            'status': new_status
        }
        
        result, error = self.make_admin_request('PUT', f'/admin/orders/{int(order_id)}/status', update_data)
        
        if error:
            print(f"Error: {error}")
        else:
            print(f"Order status updated to '{new_status}' successfully!")
        
        input("Press Enter to continue...")

    def view_ready_orders(self):
        """View all orders that are ready for delivery"""
        print("\n--- Orders Ready for Delivery ---")
        result, error = self.make_admin_request('GET', '/admin/orders/ready')
        
        if error:
            print(f"Error: {error}")
        else:
            orders = result.get('orders', [])
            if orders:
                for order in orders:
                    print(f"\nOrder ID: {order['order_id']}")
                    print(f"Customer: {order['user_name']}")
                    print(f"Store: {order['store_name']}")
                    print(f"Total: ${order['total_amount']:.2f}")
                    print(f"Address: {order['delivery_address']}")
                    print("-" * 40)
            else:
                print("No orders ready for delivery.")
        
        input("Press Enter to continue...")

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.token = None
        print("Logged out successfully!")
        input("Press Enter to continue...")
    
    def run(self):
        """Main CLI loop"""
        print("Welcome to CUHKSZ Food Ordering System!")
        
        while True:
            try:
                self.display_menu()
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")


if __name__ == '__main__':
    # Test API connection
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            print("API server is running!")
        else:
            print("Warning: Cannot connect to API server")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API server. Please make sure the server is running.")
        print("Run: python app.py")
        sys.exit(1)
    
    cli = FoodOrderingCLI()
    cli.run()