from models import db, User
from app import app

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print(f"Admin user found: {admin_user.username}, is_admin: {admin_user.is_admin}")
        # Check password
        if admin_user.check_password('admin123'):
            print("Password is correct.")
        else:
            print("Password is incorrect. Updating password...")
            admin_user.set_password('admin123')
            db.session.commit()
            print("Password updated to 'admin123'")
    else:
        print("Admin user not found. Creating...")
        admin = User(username='admin', email='admin@acadshop.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: admin, password: admin123")
