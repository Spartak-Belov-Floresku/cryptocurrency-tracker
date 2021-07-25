from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from wtforms.validators import InputRequired, Email

import uuid # ganerate values for salt and public id


bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):

    db.app = app
    db.init_app(app)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(30), primary_key=True, unique=True)
    full_name = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    public_id = db.Column(db.Text, primary_key=True, nullable=False)


    @classmethod
    def register(cls, username, full_name, password):
        """register user"""

        salt_value = str(uuid.uuid4())
        public_id = str(uuid.uuid4())

        #add solt to the password
        salted_password = salt_value+password

        password_hash = bcrypt.generate_password_hash(salted_password)

        # turn bytestring into normal (unicode utf8) str
        password_utf8_hash = password_hash.decode("utf8")
        
        #insert user into db
        user = User(username=username, full_name=full_name, password=password_utf8_hash, public_id=public_id)
        db.session.add(user)
        db.session.commit()

        #insert solt into db
        salt = Salt(user_id=user.id, value=salt_value)
        db.session.add(salt)
        db.session.commit()

        session["public_id"]=public_id

        return user


    @classmethod
    def authenticate(cls, username, pwd):
        """validate if user exits and password matches"""

        user = User.query.filter_by(username=username).first()

        if user:
            # retriving solt from databse for the user
            salt = user.salt[0].value

            #make solter password
            salted_password = salt+pwd

        if user and bcrypt.check_password_hash(user.password, salted_password):
            
            public_id = str(uuid.uuid4())
            user.public_id = public_id
            #if user passed check, creating a new public id value for the session

            db.session.commit()

            # add a new public id value to the session
            session["public_id"]=public_id

            return user

        return False
    
    @classmethod
    def save_updated_data(cls, user_obj):
        """save updated data for the user"""

        db.session.add(user_obj)
        db.session.commit()



class RecoverPassword(db.Model):

    __tablename__ = 'recover_password'

    pin = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(30), primary_key=True, unique=True)



class Salt(db.Model):

    __tablename__ = 'salts'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    value = db.Column(db.Text, nullable=False, unique=True)

    user = db.relationship('User', backref = 'salt')


class Img(db.Model):

    __tablename__ = 'images'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

    user = db.relationship('User', backref = 'img')

    @classmethod
    def save_img(cls, user_id, image):

        images = Img.query.filter_by(user_id=user_id).first()

        if not images:
            images = Img(user_id=user_id, image=image)
        else:
            images.image=image

        db.session.add(images)
        db.session.commit()

        return images



class userEmail(db.Model):

    __tablename__ = "user_emails"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    code_verified = db.Column(db.String(4))
    verified = db.Column(db.Boolean, default=False, nullable=False)


    user = db.relationship('User', backref = 'email')



class userPhone(db.Model):

    __tabelname__ = "user_phones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, unique=True, nullable=False)
    number = db.Column(db.String(10), unique=True, nullable=False)
    provider = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    code_verified = db.Column(db.String(4))
    verified = db.Column(db.Boolean, default=False, nullable=False)


    user = db.relationship('User', backref = 'phone')


class Provider(db.Model):
    
    __tablename__ = "providers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    value = db.Column(db.String(30), nullable=False)


class UserCoinsForFrontEnd(db.Model):

    __tablename__ = "user_coins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    coin_symbol = db.Column(db.String(10), nullable=False)


class TrackingCoins(db.Model):

    __tablename__ = "tracking_coins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    coin_symbol = db.Column(db.String(10), nullable=False)
    user_rate = db.Column(db.String(20), nullable=False)
    by_email = db.Column(db.String(5), default=False, nullable=False)
    by_phone = db.Column(db.String(5), default=False, nullable=False)
    goes = db.Column(db.String(5), primary_key=True, nullable=False)

    user = db.relationship('User', backref = 'tracking_coins')