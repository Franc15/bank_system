from flask_sqlalchemy import SQLAlchemy
import os

# DB_USER = os.environ['DATABASE_USER']
# DB_PASS = os.environ['DATABASE_PASSWORD']
# DB_NAME = os.environ['DATABASE_NAME']
# DB_PORT = os.environ['DATABASE_PORT']
# DB_HOST = os.environ['DATABASE_HOST']

# database_path = 'postgresql://{}/{}'.format(''+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT, DB_NAME)
database_path = 'postgresql://postgres:admin123@194.195.119.7:5432/test_erp'

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class User(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    login = db.Column(db.String(120))
    passhash = db.Column(db.String())

    
class Customer(User):
    __tablename__ = 'customers'
    email = db.Column(db.String(120))
    reg_date = db.Column(db.Date())
    accounts = db.relationship('Account', backref='customer')

    def __repr__(self):
        return f'<Customer: {self.name}, id: {self.id} >'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'login': self.login,
            'email': self.email,
            'reg_date': self.reg_date
        }

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    opening_date = db.Column(db.Date())
    balance = db.Column(db.Numeric(10, 2))
    type = db.Column(db.Integer, db.ForeignKey('account_types.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "branch_address": self.branch.address,
            "customer_id": self.customer.id,
            "balance": self.balance,
            "type": self.account_type.serialize()['description']
        }

class AccountType(db.Model):
    __tablename__ = 'account_types'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    interest_rate = db.Column(db.Float)
    accounts = db.relationship('Account', backref='account_type')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "interest_rate": self.interest_rate
        }

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    accounts = db.relationship('Account', backref='branch')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'phone': self.phone
        }

