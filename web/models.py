from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from web import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_users(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_working = db.Column(db.Boolean, nullable=False, default=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    __tablename__ = "user"
    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})
    def __repr__(self):
        return f"User('{self.id}', '{self.phone_no}', '{self.username}', '{self.email}', '{self.is_working}')"

class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Order(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_items = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    __tablename__ = "order"

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    __tablename__ = "customer"
