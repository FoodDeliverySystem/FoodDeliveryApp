from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from web import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_users(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_working = db.Column(db.Boolean, nullable=False, default=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
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
    user = db.relationship('User')
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
    user = db.relationship('Role')

class Order(db.Model, UserMixin):
    __tablename__ = "orders"
    # Order Details
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    order_items = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # User/Agent details
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('user', lazy='dynamic'))
    # Customer details
    cust_name = db.Column(db.String(30), nullable=False)
    cust_phone_no = db.Column(db.String(15), nullable=False)
    cust_addr1 = db.Column(db.String(65), nullable=False)
    cust_addr2 = db.Column(db.String(65), nullable=True)
    cust_pincode = db.Column(db.String(12), nullable=False)

# class Customer(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     c_name = db.Column(db.String(30), unique=True, nullable=False)
#     c_phone_no = db.Column(db.String(15), unique=True, nullable=False)
#     c_address_line1 = db.Column(db.String(120), nullable=False)
#     c_address_line2 = db.Column(db.String(120), nullable=True)
#     c_pincode = db.Column(db.String(12), nullable=False)
#     __tablename__ = "customer"
