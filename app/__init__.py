from flask import Flask, jsonify, request, abort
from models import setup_db, AccountType, Customer, Branch, Account, TransactionType, Transaction
import bcrypt
from datetime import datetime
from flask_cors import CORS

import os

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    setup_db(app)

    CORS(app)

    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
    # app.config['JWT_SECRET_KEY'] = 'fdsfwegwegwgeeerwg'
    jwt = JWTManager(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    @app.route('/customers', methods=['GET', 'POST'])
    def handle_users():
        if request.method == 'POST':
            body = request.get_json()

            # check if any of the fields are empty
            check_user_reg_empty_fields(body)
            
            # hashed_password = bcrypt.hashpw(body.get('password').encode('utf-8'), bcrypt.gensalt())

            new_customer = Customer(
                name=body.get('name'),
                phone=body.get('phone'),
                login=body.get('login'),
                email=body.get('email'),
                reg_date=datetime.now(),
                passhash=body.get('password')
            )

            new_customer.insert()

            return jsonify({
                'success': True,
                'customer': new_customer.serialize()
            })
        elif request.method == 'GET':
            customers = Customer.query.all()
            return jsonify([customer.serialize() for customer in customers])

    @app.route('/branches', methods=['GET', 'POST'])
    def handle_branches():
        if request.method == 'POST':
            body = request.get_json()

            new_branch = Branch(
                address=body.get('address'),
                phone=body.get('phone')
            )

            new_branch.insert()
            return jsonify({
                'status': True,
                'branch': new_branch.serialize()
            })
        elif request.method == 'GET':
            branches = Branch.query.all()
            return jsonify([branch.serialize() for branch in branches])


    @app.route('/account_types', methods=['GET', 'POST'])
    def handle_account_types():
        if request.method == 'POST':
            body = request.get_json()

            new_account_type = AccountType(
                description=body.get('description'),
                interest_rate=body.get('interest_rate')
            )

            new_account_type.insert()

            return jsonify({
                'success': True,
                'account_type': new_account_type.serialize()
            })
        elif request.method == 'GET':
            account_types = AccountType.query.all()
            return jsonify([account_type.serialize() for account_type in account_types])

    # @app.route('/accounts', methods=['GET', 'POST'])
    # def handle_accounts():
        if request.method == 'POST':
            body=request.get_json()
            customer = Customer.query.filter_by(id=body.get('customer_id')).one()
            branch = Branch.query.filter_by(id=body.get('branch_id')).one()
            account_type = AccountType.query.filter_by(id=body.get('account_type_id')).one()

            new_account = Account(
                balance=500,
                opening_date=datetime.now(),
                customer=customer,
                branch=branch,
                account_type=account_type
            )

            new_account.insert()

            return jsonify({
                'success': True,
                'new_account': new_account.serialize()
            })
        elif request.method == 'GET':
            accounts = Account.query.all()
            return jsonify([account.serialize() for account in accounts])

    @app.route('/customers/<int:customer_id>/accounts', methods=['GET', 'POST'])
    @jwt_required()
    def handle_user_account(customer_id):
        customer_identity = get_jwt_identity()
        if customer_identity != customer_id:
            abort(401)

        customer = Customer.query.filter_by(id=customer_identity).one()

        if request.method == 'POST':
            body = request.get_json()

            account_type = AccountType.query.filter_by(id=body.get('account_type_id')).one()
            branch = Branch.query.filter_by(id=body.get('branch_id')).one()

            account = Account(
                balance=500,
                opening_date=datetime.now(),
                customer=customer,
                branch=branch,
                account_type=account_type
            )

            account.insert()

            return jsonify({
                'success': True,
                'account': account.serialize()
            })
        elif request.method == 'GET':
            return jsonify({
                'success': True,
                'accounts': [account.serialize() for account in customer.accounts]
            })

    @app.route('/accounts/<int:account_id>/transactions', methods=['GET', 'POST'])
    @jwt_required()
    def handle_account_transactions(account_id):
        account = Account.query.filter_by(id=account_id).one()
        customer_identity = get_jwt_identity()

        # if customer_identity != account.customer_id:
        #     abort(401)

        if request.method == 'POST':
            body = request.get_json()

            transaction_type = TransactionType.query.filter_by(id=body.get('transaction_type_id')).one()
            to_account_id = body.get('to_account_id')

            to_account = Account.query.filter_by(id=to_account_id).one()

            transaction = Transaction(
                amount=body.get('amount'),
                datetime=datetime.now(),
                transaction_type=transaction_type,
                from_account=account,
                to_account=to_account
            )

            transaction.insert()

            to_account.balance += transaction.amount
            to_account.update()
            account.balance -= transaction.amount
            account.update()

            return jsonify({
                'success': True,
                'transaction': transaction.serialize()
            })
        elif request.method == 'GET':
            transactions = Transaction.query.filter_by(from_account_id=account_id).all()
            return jsonify({
                'success': True,
                'transactions': [transaction.serialize() for transaction in transactions]
            })


    def check_user_reg_empty_fields(body):
        if not body.get('name'):
            abort(400)
        if not body.get('phone'):
            abort(400)
        if not body.get('login'):
            abort(400)
        if not body.get('password'):
            abort(400)
        if not body.get('email'):
            abort(400)


    def check_password(password, hashed_password):
        # return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        
        if password == hashed_password:
            return True
        else:
            return False

    @app.route('/login', methods=['POST'])
    def login():
        body = request.get_json()

        customer=Customer.query.filter_by(login=body.get('username')).first()
        if customer:
            hashed=customer.passhash

            if check_password(body.get('password'), hashed):
                access_token = create_access_token(identity=customer.id)
                return jsonify({
                    'success': True,
                    'token': access_token,
                    'current_user': customer.id
                })

            else:
                return jsonify({
                    'success': False,
                    'message': 'incorrect password'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'user not exist'
            })
    
    return app
