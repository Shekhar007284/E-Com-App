from app import app
from models import db, Product, Coupon, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    if not Product.query.first():
        products = [
            Product(name="Wireless Earbuds", category="Electronics", description="Bluetooth 5.3, 24hr battery", price=1999, stock=50),
            Product(name="Mechanical Keyboard", category="Electronics", description="RGB backlit, blue switches", price=3499, stock=30),
            Product(name="Cotton T-Shirt", category="Apparel", description="100% cotton, unisex fit", price=499, stock=100),
            Product(name="Running Shoes", category="Apparel", description="Lightweight mesh, cushioned sole", price=2499, stock=40),
            Product(name="Stainless Steel Bottle", category="Home", description="1L, keeps cold 24hrs", price=699, stock=75),
            Product(name="Non-stick Pan Set", category="Home", description="3-piece set, induction compatible", price=1899, stock=20),
            Product(name="Yoga Mat", category="Fitness", description="6mm thick, non-slip", price=899, stock=60),
            Product(name="Adjustable Dumbbells", category="Fitness", description="5-25kg adjustable pair", price=4999, stock=15),
            Product(name="Novel: The Silent Patient", category="Books", description="Bestselling thriller", price=349, stock=90),
            Product(name="Desk Lamp", category="Home", description="LED, adjustable brightness", price=1299, stock=45),
        ]
        db.session.bulk_save_objects(products)

    if not Coupon.query.first():
        db.session.add(Coupon(code="SAVE10", discount_percent=10, active=True))
        db.session.add(Coupon(code="SAVE20", discount_percent=20, active=True))
        db.session.add(Coupon(code="EXPIRED5", discount_percent=5, active=False))  # deliberately inactive, for negative testing

    if not User.query.filter_by(username="admin").first():
        db.session.add(User(
            username="admin", email="admin@test.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        ))

    db.session.commit()
    print("Seed data created.")