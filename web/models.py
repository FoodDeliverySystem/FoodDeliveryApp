from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from web import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_delivery_agent(id):
    return DeliveryAgent.query.get(int(id))

@login_manager.user_loader
def load_admin(id):
    return Admin.query.get(int(id))

class DeliveryAgent(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_working = db.Column(db.Boolean, nullable=False, default=True)
    __tablename__ = "delivery_agent"
    # def __repr__(self):
    #     return f"DeliveryAgent('{self.id}', '{self.phone_no}', '{self.username}', '{self.email}', '{self.is_working}')"

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    __tablename__ = "admin"
    # def __repr__(self):
    #     return f"Admin('{self.id}', '{self.phone_no}', '{self.username}', '{self.email}', '{self.is_working}')"

class Order(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('delivery_agent.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_items = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    __tablename__ = "orders"

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    __tablename__ = "customer"
