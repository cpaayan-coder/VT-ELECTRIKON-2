import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "vt_elektrikon_secret"

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        price REAL,
        stock INTEGER,
        image TEXT
    )
    """)

    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]

    if count == 0:
        c.execute("""
        INSERT INTO products (name,brand,price,stock,image)
        VALUES
        ('Multispan Digital Timer','Multispan',1200,5,'multispan_timer.jpg'),
        ('Sibass MCB','Sibass',850,2,'sibass_mcb.jpg')
        """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM products")
    products = c.fetchall()

    conn.close()

    return render_template("index.html", products=products)


# ---------------- ADD TO CART ----------------

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", [])

    cart.append(product_id)

    session["cart"] = cart

    return redirect(url_for("cart"))


# ---------------- CART PAGE ----------------

@app.route("/cart")
def cart():

    cart_ids = session.get("cart", [])

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    products = []

    for pid in cart_ids:

        c.execute("SELECT * FROM products WHERE id=?", (pid,))
        product = c.fetchone()

        if product:
            products.append(product)

    conn.close()

    return render_template("cart.html", products=products)


# ---------------- BUY PRODUCT ----------------

@app.route("/buy/<int:product_id>")
def buy(product_id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT stock FROM products WHERE id=?", (product_id,))
    result = c.fetchone()

    if result:

        stock = result[0]

        if stock > 0:

            c.execute(
                "UPDATE products SET stock = stock - 1 WHERE id=?",
                (product_id,)
            )

            conn.commit()

            message = "Order placed successfully!"

        else:

            message = "Out of stock!"

    else:

        message = "Product not found!"

    conn.close()

    return message


# ---------------- ADMIN PANEL ----------------

@app.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        name = request.form["name"]
        brand = request.form["brand"]
        price = request.form["price"]
        stock = request.form["stock"]
        image = request.form["image"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO products (name,brand,price,stock,image)
        VALUES (?,?,?,?,?)
        """,(name,brand,price,stock,image))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("admin.html")


# ---------------- START SERVER ----------------

if __name__ == "__main__":

    init_db()

    port = int(os.environ.get("PORT",5000))

    app.run(host="0.0.0.0", port=port)