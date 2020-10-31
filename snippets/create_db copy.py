#
# Use this to create a DB
#
from web.models import *
from web import db

admin1 = Admin(username='admin', email='admin@admin.com', password='admin', phone_no='384734877')
db.session.add(admin1)
db.session.commit()