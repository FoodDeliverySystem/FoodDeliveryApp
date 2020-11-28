from flask import Blueprint
from . import db
from .models import *
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_user import roles_required
from .forms import *
import webbrowser

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

@main.route("/agent/<int:agent_id>", methods=['GET'])
@login_required
def agent(agent_id):
    agent = User.query.get_or_404(agent_id)
    orders = db.session.query(Order).filter(Order.user_id == agent_id, Order.status != OrderStatus.delivered).all()
    return render_template('agent.html', agent=agent, orders=orders)

@main.route("/current_orders", methods=['GET'])
@login_required
def current_orders():
    orders = db.session.query(Order).filter(Order.status != OrderStatus.delivered).order_by(Order.id).all()
    return render_template('orders_list.html', orders=orders, title='List of Open Orders')

@main.route("/delivered_orders", methods=['GET'])
@login_required
def delivered_orders():
    orders = db.session.query(Order).filter(Order.status == OrderStatus.delivered).order_by(Order.id).all()
    return render_template('orders_list.html', orders=orders, title='List of Delivered Orders')

@main.route("/unassigned_orders", methods=['GET'])
@login_required
def unassigned_orders():
    orders = db.session.query(Order.cust_pincode).filter(Order.user_id == None ,Order.status != OrderStatus.delivered).group_by(Order.cust_pincode).all()
    return render_template('pincode_list.html', orders=orders, title="Pincodes of open orders")

@main.route("/pin_orders/<string:pin>", methods=['GET'])
@login_required
def pin_orders(pin):
    orders = db.session.query(Order).filter(Order.user_id == None, Order.status != OrderStatus.delivered, Order.cust_pincode == pin).order_by(Order.id).all()
    title = "Orders in " + pin
    return render_template('orders_list.html', orders=orders, title=title)

# @main.route("/unassigned_orders", methods=['GET'])
# @login_required
# def unassigned_orders():
#     orders = db.session.query(Order).filter(Order.user_id == None).order_by(Order.id).all()
#     return render_template('orders_list.html', orders=orders, title='List of Un-assigned Orders')

@main.route("/order/<int:order_id>", methods=['GET'])
@login_required
def order(order_id):
    order = Order.query.get_or_404(order_id)
    agent = User.query.get(order.user_id)
    return render_template('order.html', order=order, agent=agent)

@main.route("/agent_order_view/<int:order_id>")
@login_required
def detailed_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('agent_order_view.html', order=order, agent=current_user)

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

@main.route("/update_order_status/<int:order_id>/<string:status_option>", methods=['GET', 'POST'])
@login_required
def update_order_status(order_id, status_option):
    order = Order.query.get_or_404(order_id)
    order.status = OrderStatus[status_option]
    db.session.commit()
    message_body = 'Kanishka Redmond Update\nOrder ID: {}\nStatus: {}'.format(str(order.id), str(order.status))
    # should work on iOS 8+ and Android (only for single sender and message)
    # Ref https://stackoverflow.com/questions/6480462/how-to-pre-populate-the-sms-body-text-via-an-html-link
    sms_string = 'sms:{};?&body={}'.format(str(order.phone), message_body)
    return redirect(sms_string)

@main.route("/get_order_status/<int:order_id>", methods=['GET', 'POST'])
@login_required
def get_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    return '<span class="badge badge-dark">{}</span>'.format(order.status)

@main.route("/update_order_status_agent/<int:order_id>/<string:status_option>", methods=['GET', 'POST'])
@login_required
def update_order_status_agent(order_id, status_option):
    order = Order.query.get_or_404(order_id)
    order.status = OrderStatus[status_option]
    db.session.commit()
    message_body = 'Kanishka Redmond Update\nOrder ID: {}\nStatus: {}'.format(str(order.id), str(order.status))
    sms_string = 'sms:{};?&body={}'.format(str(order.phone), message_body)
    return redirect(sms_string)

@main.route("/create_order", methods=['GET', 'POST'])
@login_required
def create_order():
    create_order_form = OrderItemsForm()
    if create_order_form.validate_on_submit(): 
        new_order = Order(status=create_order_form.status.data, cust_name=create_order_form.cust_name.data, phone=create_order_form.phone.data,cust_addr1=create_order_form.cust_addr1.data, cust_addr2=create_order_form.cust_addr2.data,cust_pincode=create_order_form.cust_pincode.data, delivery_date=create_order_form.delivery_date.data, delivery_start_time=create_order_form.delivery_start_time.data, delivery_end_time=create_order_form.delivery_end_time.data, delivery_instructions=create_order_form.delivery_instructions.data)
        db.session.add(new_order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return (redirect(url_for('main.create_order')))
    return render_template('create_order.html', form=create_order_form)

@main.route("/agent_view")
@login_required
def agent_home_page():
    print(current_user.id)
    orders = db.session.query(Order).filter(Order.user_id == current_user.id ,Order.status != OrderStatus.delivered).all()
    return render_template('agent_assigned_orders_view.html', agent=current_user, orders = orders)