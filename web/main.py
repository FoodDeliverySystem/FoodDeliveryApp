from flask import Blueprint
from . import db
from .models import *
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_user import roles_required
from .forms import *


main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.da_list'))
    else:
        return redirect(url_for('auth.login'))

@main.route("/da_list")
@roles_required('Admin')
@login_required
def da_list():
    agents = User.query.order_by(User.id).all()
    return render_template('da_list.html', agents=agents)

@main.route("/agent/<int:agent_id>")
@login_required
def agent(agent_id):
    agent = User.query.get_or_404(agent_id)
    orders = db.session.query(Order).filter(Order.user_id == agent_id, Order.status != OrderStatus.delivered).all()
    return render_template('agent.html', agent=agent, orders=orders)

@main.route("/order/<int:order_id>")
@login_required
def order(order_id):
    order = Order.query.get_or_404(order_id)
    agent = User.query.get_or_404(order.user_id)
    return render_template('order.html', order=order, agent=agent)

@main.route("/assign_view/<int:order_id>")
@login_required
def assign_view(order_id):
    agents = User.query.filter_by(is_working=True)
    return render_template('assign_view.html', agents=agents, order_id=order_id)

@main.route("/assign_order/<int:order_id>/<int:user_id>")
@login_required
def assign_order(order_id, user_id):
    order = Order.query.get_or_404(order_id)
    order.user_id = user_id
    db.session.commit()
    return redirect(url_for('main.agent', agent_id=user_id))

@main.route("/da_update_status/<int:agent_id>")
@login_required
def da_update_status(agent_id):
    agent = User.query.get_or_404(agent_id)
    agent.is_working = not agent.is_working
    db.session.commit()
    return (redirect(url_for('main.agent', agent_id=agent.id)))

@main.route("/da_list/create_order", methods=['GET', 'POST'])
@login_required
def create_order():
    create_order_form = OrderItemsForm()
    if create_order_form.validate_on_submit(): 
        new_order = Order(order_items=create_order_form.order_items.data, status=create_order_form.status.data)
        db.session.add(new_order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return render_template('create_order.html', form=create_order_form)
    elif create_order_form.validate() == False:
        print("error")
        flash('Error in Order Validation!', 'danger')
    return render_template('create_order.html', form=create_order_form)