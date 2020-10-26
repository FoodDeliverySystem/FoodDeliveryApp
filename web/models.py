from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_delivery_agent(agent_id):
    return DeliveryAgent.query.get(int(agent_id))

@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))

class DeliveryAgent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_working = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f"DeliveryAgent('{self.id}', '{self.username}', '{self.email}', '{self.is_working}')"

# class Order(db.Model, UserMixin):
