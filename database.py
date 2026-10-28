
import sqlite3

def init_db():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS order_items')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS menu_items')
    cursor.execute('DROP TABLE IF EXISTS categories')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    cursor.execute('CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)')
    
    cursor.execute('''
        CREATE TABLE menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category_id INTEGER,
            image TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Updated with fulfillment tracking column metrics
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            fulfillment_type TEXT NOT NULL,
            fulfillment_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_item_id INTEGER,
            quantity INTEGER NOT NULL,
            price_at_purchase REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
        )
    ''')
    
    categories = [('Appetizers',), ('Main Course',), ('Desserts',),('Beverages',)]
    cursor.executemany('INSERT INTO categories (name) VALUES (?)', categories)
            
    cursor.execute("SELECT id FROM categories WHERE name = 'Appetizers'")
    app_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM categories WHERE name = 'Main Course'")
    main_id = cursor.fetchone()[0]
        
    cursor.execute("SELECT id FROM categories WHERE name = 'Desserts'")
    dess_id = cursor.fetchone()[0]
        
    cursor.execute("SELECT id FROM categories WHERE name = 'Beverages'")
    bev_id = cursor.fetchone()[0]
         
    items = [
                         ('French Fries', 'Golden, Crispy, Traditional-cut fries.', 5.99, app_id, 'French_Fries.jpeg'),
                         ('Biryani', 'Served with aged basmati rice, Chicken and seasonal vegetables.', 18.99, main_id, 'biryani.jpeg'),
                         ('Kombucha Tea', ' A fermented, effervescent and sweetened black tea drink.', 1.99, bev_id, 'kombucha.jpeg'),
                         ('Swiss Roll Cake ', 'A rich chocolate sponge cake  spiraled around a light, fluffy whipped cream filling and coated with chocolate glaze.', 4.99, dess_id, 'swiss_cake.jpg')
                     
                     ]
           
    cursor.executemany('INSERT INTO menu_items (title, description, price, category_id, image) VALUES (?, ?, ?, ?, ?)', items)
        
    conn.commit()
    conn.close()
    print("Database columns rebuilt successfully for multi-fulfillment tracking lines!")

if __name__ == '__main__':
    init_db()




    
             
        