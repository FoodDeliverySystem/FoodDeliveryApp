from flask import Blueprint
from . import db
from .models import *
from flask import Blueprint, render_template, redirect, url_for, flash, escape, request
from flask_login import login_required, current_user
from flask_user import roles_required
from .forms import *
from urllib.parse import quote
from sqlalchemy import func
import time
from datetime import datetime, timedelta
from flask import jsonify

from pytz import timezone
import pytz
main = Blueprint('main', __name__)

@app.errorhandler(403)
def unauthorized(e):
    return render_template('error_page.html', error_code=403, error_message='You are not allowed to access this page!'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_page.html', error_code=404, error_message='Page Not Found!'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error_page.html', error_code=500, error_message='Internal Server Error!'), 500

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.has_roles('Admin'):
            return redirect(url_for('main.da_list'))
        else:
            return redirect(url_for('main.agent_view'))
    else:
        return redirect(url_for('auth.login'))

@main.route("/da_list")
@roles_required('Admin')
@login_required
def da_list():
    agent_role = Role.query.filter_by(name='Agent').first()
    agents = db.session.query(User).filter(User.roles.contains(agent_role))
    return render_template('da_list.html', agents=agents)

@main.route("/agent/<int:agent_id>", methods=['GET'])
@roles_required('Admin')
@login_required
def agent(agent_id):
    agent = User.query.get_or_404(agent_id)
    orders = db.session.query(Order).filter(Order.user_id == agent_id, Order.status != OrderStatus.delivered).all()
    return render_template('agent.html', agent=agent, orders=orders)

@main.route("/current_orders", methods=['GET'])
@roles_required('Admin')
@login_required
def current_orders():
    page = request.args.get('page', 1 , type=int)
    orders = db.session.query(Order).filter(Order.status != OrderStatus.delivered).order_by(Order.id).paginate(page=page, per_page=8)
    return render_template('orders_list.html', orders=orders, title='List of Open Orders', base_func='current_orders', delivery_status= OrderStatus.delivered)

@main.route("/delivered_orders", methods=['GET'])
@roles_required('Admin')
@login_required
def delivered_orders():
    page = request.args.get('page', 1 , type=int)
    # Delivered orders need to be in descending
    orders = db.session.query(Order).filter(Order.status == OrderStatus.delivered).order_by(Order.id.desc()).paginate(page=page, per_page=8)
    return render_template('orders_list.html', orders=orders, title='List of Delivered Orders', base_func='delivered_orders', delivery_status= OrderStatus.delivered)

@main.route("/unassigned_orders", methods=['GET'])
@roles_required('Admin')
@login_required
def unassigned_orders():
    orders = db.session.query(Order.cust_pincode).filter(Order.user_id == None ,Order.status != OrderStatus.delivered).group_by(Order.cust_pincode).all()
    return render_template('pincode_list.html', orders=orders, title="Pincodes of open orders")

@main.route("/pin_orders/<string:pin>", methods=['GET'])
@roles_required('Admin')
@login_required
def pin_orders(pin):
    page = request.args.get('page', 1 , type=int)
    orders = db.session.query(Order).filter(Order.user_id == None, Order.status != OrderStatus.delivered, Order.cust_pincode == pin).order_by(Order.id).paginate(page=page, per_page=8)
    title = "Orders in " + pin
    agent_role = Role.query.filter_by(name='Agent').first()
    agents = db.session.query(User).filter(User.roles.contains(agent_role))
    return render_template('orders_list.html', orders=orders, title=title, base_func='pin_orders', delivery_status= OrderStatus.delivered, agents=agents)

@main.route("/order/<int:order_id>", methods=['GET'])
@roles_required('Admin')
@login_required
def order(order_id):
    order = Order.query.get_or_404(order_id)
    agent = User.query.get(order.user_id)
    return render_template('order.html', order=order, agent=agent)

@main.route("/agent_order_view/<int:order_id>")
@roles_required('Agent')
@login_required
def detailed_order(order_id):
    order = Order.query.get_or_404(order_id)
    complete_address = order.cust_addr1
    if order.cust_addr2:
        complete_address = complete_address + ' ' + order.cust_addr2
    complete_address = complete_address + ' ' + order.cust_pincode
    # making the address url safe
    escaped_address = escape(complete_address)
    return render_template('agent_order_view.html', order=order, agent=current_user, escaped_address=escaped_address, delivery_status= OrderStatus.delivered)

@main.route("/plot_agent_route/<int:agent_id>")
@roles_required('Agent')
@login_required
def plot_agent_route(agent_id):
    orders = db.session.query(Order.cust_addr1, Order.cust_addr2, Order.cust_pincode).filter(Order.user_id == agent_id, Order.status != OrderStatus.delivered).all()
    gapi_prefix = r'https://www.google.com/maps/dir//'
    #gapi_prefix = r'https://www.google.com/maps/dir/?api=1&origin=16651+Redmond+way,Redmond,+WA+98052&waypoints='
    waypoints = ''
    for order in orders:
        order_address = order.cust_addr1 + ' '
        if order.cust_addr2:
            order_address = order_address + ' ' + order.cust_addr2
        order_address = order_address + order.cust_pincode
        #waypoints = waypoints + order_address + '|'
        waypoints = waypoints + order_address + '/'
    gapi_route = gapi_prefix + quote(waypoints)
    #print("GMAPS API CALL:" + gapi_route)
    return redirect(gapi_route)

@main.route("/plot_uo_route")
@roles_required('Admin')
@login_required
def plot_uo_route():
    orders = db.session.query(Order.cust_addr1, Order.cust_addr2, Order.cust_pincode).filter(Order.user_id == None).all()
    gapi_prefix = r'https://www.google.com/maps/dir//'
    waypoints = ''
    for order in orders:
        order_address = order.cust_addr1 + ' '
        if order.cust_addr2:
            order_address = order_address + ' ' + order.cust_addr2
        order_address = order_address + order.cust_pincode
        waypoints = waypoints + order_address + '/'
    gapi_route = gapi_prefix + quote(waypoints)
    return redirect(gapi_route)

@main.route("/assign_view/<int:order_id>")
@roles_required('Admin')
@login_required
def assign_view(order_id):
    agents = User.query.filter_by(is_working=True)
    return render_template('assign_view.html', agents=agents, order_id=order_id)

@main.route("/assign_order/<int:order_id>/<int:user_id>")
@roles_required('Admin')
@login_required
def assign_order(order_id, user_id):
    order = Order.query.get_or_404(order_id)
    if user_id == 0:
        order.user_id = None
        flash('Order un-assigned successfully!', 'info')
    else:
        order.user_id = user_id
        flash('Order assigned successfully!', 'success')
    db.session.commit()
    return redirect(url_for('main.unassigned_orders'))

@main.route("/assign_multiple_orders", methods=['POST'])
@roles_required('Admin')
@login_required
def assign_multiple_orders():
    if request.method == 'POST':
        args = request.get_json()
        order_ids = args['orderId']
        agent_id = args['agentId']
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        for order in orders:
            order.user_id = agent_id
        db.session.commit()
        flash('Orders assigned successfully!', 'success')
        print("redirecting")
        return jsonify(dict(redirect='/unassigned_orders'))

@main.route("/delete_multiple_orders", methods=['POST'])
@roles_required('Admin')
@login_required
def delete_multiple_orders():
    if request.method == 'POST':
        args = request.get_json()
        order_ids = args['orderId']
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        for order in orders:
            db.session.delete(order)
            print("Deleting")
        db.session.commit()
        flash('Orders deleted successfully!', 'success')
        print("redirecting")
        return jsonify(dict(redirect='/unassigned_orders'))

@main.route("/da_update_status/<int:agent_id>")
@login_required
def da_update_status(agent_id):
    agent = User.query.get_or_404(agent_id)
    agent.is_working = not agent.is_working
    db.session.commit()
    return (redirect(url_for('main.agent', agent_id=agent.id)))

@main.route("/update_order_status/<int:order_id>/<string:status_option>", methods=['GET', 'POST'])
@roles_required('Admin')
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
@roles_required('Agent')
@login_required
def update_order_status_agent(order_id, status_option):
    order = Order.query.get_or_404(order_id)
    order.status = OrderStatus[status_option]
    db.session.commit()
    message_body = 'Kanishka Redmond Update\nOrder ID: {}\nStatus: {}'.format(str(order.id), str(order.status))
    sms_string = 'sms:{};?&body={}'.format(str(order.phone), message_body)
    return redirect(sms_string)

@main.route("/create_order", methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def create_order():
    create_order_form = OrderItemsForm()
    if create_order_form.validate_on_submit(): 
        new_order = Order(status=create_order_form.status.data, cust_name=create_order_form.cust_name.data, phone=create_order_form.phone.data, cust_addr1=create_order_form.cust_addr1.data, cust_addr2=create_order_form.cust_addr2.data, cust_pincode=create_order_form.cust_pincode.data.strip(), delivery_instructions=create_order_form.delivery_instructions.data, user_tip=create_order_form.user_tip.data, drinks=create_order_form.drinks.data)
        db.session.add(new_order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return (redirect(url_for('main.create_order')))
    return render_template('create_order.html', form=create_order_form)

@main.route("/edit_order/<int:order_id>", methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status=OrderStatus(order.status).name
    edit_order_form = OrderItemsForm(obj=order)
    if edit_order_form.validate_on_submit():
        update_existing_order(order, edit_order_form)
        db.session.commit()
        flash('Order updated successfully!', 'success')
        return (redirect(url_for('main.current_orders')))
    return render_template('edit_order.html', form=edit_order_form, order_id=order_id)

@main.route("/delete_order/<int:order_id>", methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash('Order Deleted successfully!', 'success')
        return (redirect(url_for('main.current_orders')))
    agent = User.query.get(order.user_id)
    return render_template('order.html', order=order, agent=agent)

def update_existing_order(order, form):
    order.status = form.status.data
    order.cust_name = form.cust_name.data
    order.phone = form.phone.data
    order.cust_addr1 = form.cust_addr1.data
    order.cust_addr2 = form.cust_addr2.data
    order.cust_pincode = form.cust_pincode.data.strip()
    order.delivery_instructions = form.delivery_instructions.data
    order.user_tip = form.user_tip.data
    order.drinks = form.drinks.data

@main.route("/agent_view")
@login_required
def agent_view():
    page = request.args.get('page', 1 , type=int)
    orders = db.session.query(Order).filter(Order.user_id == current_user.id ,Order.status != OrderStatus.delivered).paginate(page=page, per_page=8)
    return render_template('agent_assigned_orders_view.html', agent=current_user, orders = orders, page=page, delivery_status= OrderStatus.delivered)

@main.route("/agent_dorders", methods=['GET'])
@roles_required('Agent')
@login_required
def agent_dorders():
    page = request.args.get('page', 1 , type=int)
    orders = db.session.query(Order).filter(Order.status == OrderStatus.delivered, Order.user_id == current_user.id).order_by(Order.id.desc()).paginate(page=page, per_page=8)
    agent = User.query.get_or_404(current_user.id)
    return render_template('agent_dorders.html', orders=orders, agent=agent,title='List of Delivered Orders', page=page, delivery_status= OrderStatus.delivered)

def time_to_datetime(time, from_tz='US/Pacific', to_tz='UTC'):
    # converts datetime.time to datetime obj
    time = datetime.combine(time, datetime.min.time(), tzinfo=timezone(from_tz))
    # change timezone
    # time = time.astimezone(timezone(to_tz))
    return time

@main.route("/agent_tips", methods=['GET', 'POST'])
@roles_required('Agent')
@login_required
def agent_tips():
    tip_form = AgentTipForm()
    if tip_form.validate_on_submit():
        # From 12:00 AM of start date to 11:59 PM of end date
        start_date = time_to_datetime(tip_form.start_date.data).replace(hour=0, minute=0)
        end_date = time_to_datetime(tip_form.end_date.data).replace(hour=23, minute=59)
        res = db.session.query(func.sum(Order.user_tip).label('tip_sum'), func.count(Order.id).label('order_count')).filter(Order.user_id == current_user.id, Order.date >= start_date, Order.date <= end_date).first()
        tip_sum = res.tip_sum
        order_count = res.order_count
        if tip_sum:
            tip_sum = '{0:.3f}'.format(tip_sum)
        else:
            tip_sum = None
        agent = User.query.get_or_404(current_user.id)
        flash('Calculated from 12:00 AM PST of start date to 11:59 PM PST of end date.', 'info')
        return render_template('tips.html', tip_sum=tip_sum, order_count=order_count, start_date=start_date, end_date=end_date, agent=agent, layout="agent_layout.html")
    return render_template('agent_tips.html', form=tip_form)

@main.route("/admin_tips", methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def admin_tips():
    tip_form = AdminTipForm()
    tip_form.agent_id.choices = [ (agent.id, agent.username) for agent in User.query.filter(User.id!=current_user.id).all() ]
    if tip_form.validate_on_submit():
        agent_id = tip_form.agent_id.data
        # From 12:00 AM of start date to 11:59 PM of end date
        start_date = time_to_datetime(tip_form.start_date.data).replace(hour=0, minute=0)
        end_date = time_to_datetime(tip_form.end_date.data).replace(hour=23, minute=59)
        res = db.session.query(func.sum(Order.user_tip).label('tip_sum'), func.count(Order.id).label('order_count')).filter(Order.user_id == agent_id, Order.date >= start_date, Order.date <= end_date).first()
        tip_sum = res.tip_sum
        order_count = res.order_count
        if tip_sum:
            tip_sum = '{0:.3f}'.format(tip_sum)
        else:
            tip_sum = None
        agent = User.query.get_or_404(agent_id)
        flash('Calculated from 12:00 AM PST of start date to 11:59 PM PST of end date.', 'info')
        return render_template('tips.html', tip_sum=tip_sum, order_count=order_count, start_date=start_date, end_date=end_date, agent=agent, layout="admin_layout.html")
    return render_template('admin_tips.html', form=tip_form)
