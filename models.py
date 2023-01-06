from flask_sqlalchemy import SQLAlchemy

database_name = 'test_erp'
database_path = 'postgresql://{}/{}'.format('postgres:admin123@194.195.119.7:5432', database_name)

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

    def __repr__(self):
        return f'<Customer: {self.name}, id: {self.id} >'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'login': self.login,
            'email': self.email,
            'reg_date': self.reg_date
        }

