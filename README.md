# food_ordering_system_simulator
This is a full-stack campus food delivery system designed for The Chinese University of Hong Kong, Shenzhen, utilizing a frontend-backend separation architecture. The backend of the project is built using the Flask framework to create a RESTful API, with SQLAlchemy for ORM database management, while the frontend features a CLI.
System Requirements
Python 3.7+

Project Structure
csc3170_food_ordering/
├── app.py                 # Flask main application file
├── models.py              # Database model definitions
├── config.py              # Application configuration file
├── cli_client.py          # CLI frontend client
├── init_db.py             # Database initialisation script
├── requirements.txt       # Project dependencies file
└── utils/                 # Utility package
    ├── __init__.py
    └── auth.py            # Authentication utility functions

Programme Operation Instructions

pip (Python package manager)
Install Project Dependencies

pip install -r requirements.txt
Initialize Database

python init_db.py
This will create database tables and insert sample data.

Start Backend Server
python app.py
The server will start at http://localhost:5000.

Start CLI Client (New Terminal Window)
python cli_client.py

Test Accounts
The system has pre-configured the following test accounts:

User Account
Username: student1

Password: password123

Administrator Account
Username: admin1

Password: admin123

User Guide
User Functions
Register New Account - Create a personal account
Login to System - Log in using username and password
Browse Shops - View all available restaurants
View Menu - Browse items from specific shops
Shopping Cart Management - Add/remove items to shopping cart
Place Order - Create an order from shopping cart
Order Management - View order history, modify unshipped orders, confirm receipt
Personal Information - View and modify personal details

Administrator Functions
Order Management - View all orders, update order status
Shop Management - Add, modify, delete shops
Delivery Personnel Management - Add, delete delivery personnel
Order Allocation - Assign orders to delivery personnel

