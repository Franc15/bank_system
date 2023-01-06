from flask import Flask, jsonify, request, abort
from models import setup_db, User, Customer
import bcrypt

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    setup_db(app)

    # CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    @app.route('/users', methods=['GET', 'POST'])
    def handle_users():
        if request.method == 'POST':
            body = request.get_json()

            # check if any of the fields are empty
            check_empty_fields(body)

            password = body.get('password')
            
            hashed_password = bcrypt.hashpw(body.get('password').encode('utf-8'), bcrypt.gensalt())
    
            new_customer = Customer(
                first_name=body.get('first_name'),
                last_name=body.get('last_name'),
                dob=body.get('dob'),
                gender = body.get('gender'),
                email=body.get('email'),
                password=hashed_password,
                address=body.get('address'),
                employer=body.get('employer'),
                job_title=body.get('job_title')
            )
            new_customer.insert()

            return jsonify({
                'success': True,
                'user': new_customer.serialize()
            })
        elif request.method == 'GET':
            users = User.query.all()
            return jsonify([user.serialize() for user in users])

    def check_empty_fields(body):
        if not body.get('first_name'):
            abort(400)
        if not body.get('last_name'):
            abort(400)
        if not body.get('dob'):
            abort(400)
        if not body.get('gender'):
            abort(400)
        if not body.get('email'):
            abort(400)
        if not body.get('password'):
            abort(400)


    # def check_password(password, hashed_password):
    #     return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    return app
