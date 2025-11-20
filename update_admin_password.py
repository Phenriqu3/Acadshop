from models import db, User
from app import app

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.set_password('admin123')
        db.session.commit()
        print('Password updated successfully')
    else:
        print('Admin user not found')
