


🍔 Fatima Bistro Bites — Restaurant Ordering System

Project Overview

A professional, full-stack Python Flask web application featuring a functional menu presentation directory and an 
interactive shopping cart. The platform handles user persistence safely on the server side via cryptographic session 
signatures, processing item counts, quantity alterations, dynamic filtering, and complete transaction calculations 
inside a lightweight SQLite layout.

Key Features

• CSS Grid-Aligned Layout: Implements uniform card frameworks via responsive grid fractions (repeat(auto-fill, minmax(280px, 1fr))), ensuring all card items sit securely on a uniform line.

• Server-Controlled State Engine: Keeps active user choices alive through secure Flask Sessions (flask.session), preventing structural shopping list vulnerabilities or client data manipulation.

• Granular Lifecycle CRUD Controls: Establishes granular route mechanics (/cart/add, /cart/update, /cart/clear) matching SQL transactions to let users expand item volumes or drop records permanently.

• Dynamic Database Initialization: Hooks directly into native SQLite modules, systematically scanning and auto-generating standard product listings upon application launch if table states return vacant.

Technical Specifications

• Backend: Python, Flask Framework, Jinja2 Templating, Flask Sessions
• Database: SQLite / SQLAlchemy Object-Relational Mapping (ORM)
• Frontend: HTML5 Forms, CSS Grid Layout (ensuring inline card alignment), Media Queries

✨ Features


🍽️ Customer Experience

• Dynamic Category Menu Bar: Horizontal scrollable category navigation bar pinned to the top with smooth-scrolling jump anchors.
• ***Sticky Right-Side Shopping Cart: A persistent, scroll-locked summary sidebar featuring quantity controls, automatic subtotal/tax calculations, and a quick-clear tool.
• Multi-Fulfillment Checkout: Choose between Dine-In (with table number entry), Takeout (pickup), or Delivery (with address entry).
• Customer Authentication: Secure password hashing (using werkzeug.security) for user sign-up, sign-in, and session management.
• Personal Order History (/profile): Logged-in customers can view past receipts, track kitchen statuses (Pending, Cooking, Completed), and expand orders to inspect itemized breakdowns of dishes and quantities purchased.
• Simulated Payment Gateway: A clean, 256-bit SSL-styled mock credit card processing screen that logs validated orders directly into the database.



👨‍🍳 Admin & Staff Dashboard (/admin)

• Staff Login Protection: Dedicated admin authentication layer.
• Menu Item Management: Add new dishes with titles, descriptions, pricing, categories, and image uploads.
• Live Kitchen Order Queue: View incoming customer orders, inspect fulfillment types (Table/Address/Takeout), and update order states in real-time via status dropdowns (Pending → Cooking → Completed).




The following structure breaks down the active project landscape:


project/
│
├── app.py                  # Python application logic & routes
├── database.py             # Database creation & initialization script
├── restaurant.db           # SQLite database file (auto-generated)
│
├── static/
│   └── style.css           # Custom CSS for styling the application
|   └── uploads/            # Create this folder to store uploade images
|
│
└── templates/
    ├── base.html           # Master layout template
    ├── menu.html           # Public digital menu page
    ├── login.html          # Admin login page
    └── admin.html          # Admin dashboard (CRUD panel)
    ├── customer_login.html # Customer Credentials to order
    ├── profile.html        # Profile page for customer history
    ├── register.html       # Create an account or sign up 
    └── payment.html        # Payment Gateway




📂 Modular Project Source Blueprint
    


1. Database Configuration, Core Methods and Application Engine Router :


 *** database.py ***

Data connection access points running pure raw optimized SQL operations.
     
   *** (app.py) ***

Handles initialization, session lifecycle hooks, customer storefront rendering, cart mutations, and admin access controls.


2. Administration Hub (templates/cart.html)


3. Frontend Layout Template (templates/base.html)

This provides a modern, clean  navigation framework matching professional admin and retail configurations.

4. Menu & Grid Display Template (templates/menu.html)


5. Shopping Cart Interface Template (templates/cart.html)


6. Customer Loging to Place an Order (templates/customer_login.html)
7. Sign up or Create an account for new customer (temlates/register.html)
8. Customer Profile to retrieve order history (templates/profile.html)
9. Payment Gateway (templates/payment.html)