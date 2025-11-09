import os
from werkzeug.security import generate_password_hash

from app import app, db, User


def init_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Created admin user: username=admin password=admin123')
        else:
            print('Admin user already exists:', admin.username)


if __name__ == '__main__':
    init_db()
