from flask_sqlalchemy import SQLAlchemy
import os
import bcrypt

# DB_USER = os.environ['DATABASE_USER']
# DB_PASS = os.environ['DATABASE_PASSWORD']
# DB_NAME = os.environ['DATABASE_NAME']
# DB_PORT = os.environ['DATABASE_PORT']
# DB_HOST = os.environ['DATABASE_HOST']

DB_USER = 'postgres'
DB_PASS = 'franc123'
DB_NAME = 'test_erp'
DB_PORT = '5432'
DB_HOST = 'localhost'

database_path = 'postgresql://{}/{}'.format(''+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT, DB_NAME)

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
    passhash = db.Column(db.Text)

    
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
    account_no = db.Column(db.String(120))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    opening_date = db.Column(db.Date())
    balance = db.Column(db.Numeric(10, 2))
    type = db.Column(db.Integer, db.ForeignKey('account_types.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "branch_address": self.branch.address,
            "customer_id": self.customer.id,
            "balance": self.balance,
            "account_no": self.account_no,
            "type": self.account_type.serialize()['description']
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2))
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    from_account = db.relationship('Account', foreign_keys=[from_account_id], backref='from_account')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], backref='to_account')
    datetime = db.Column(db.Date())
    type = db.Column(db.Integer, db.ForeignKey('transaction_types.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "from_account_id": self.from_account_id,
            "from_account": self.from_account.serialize(),
            "to_account_id": self.to_account_id,
            "datetime": self.datetime,
            "type": self.transaction_type.description
        }


class TransactionType(db.Model):
    __tablename__ = 'transaction_types'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(20))
    transactions = db.relationship('Transaction', backref='transaction_type')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description
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

