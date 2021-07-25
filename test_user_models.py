"""User models tests."""


from unittest import TestCase
from random import sample
from werkzeug.datastructures import FileStorage
import base64
import io

from app import app
from models import db, User, RecoverPassword, Salt, Img, userEmail, userPhone,  UserCoinsForFrontEnd, TrackingCoins, Provider
from helper import UserSession

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_tracker'

db.create_all()


class UserModelTestCase(TestCase):

    def setUp(self):
        """before each test of the method deleting data from tables"""

        RecoverPassword.query.delete()
        UserCoinsForFrontEnd.query.delete()
        TrackingCoins.query.delete()
        Salt.query.delete()
        Img.query.delete()
        userEmail.query.delete()
        userPhone.query.delete()
        User.query.delete()

        Provider.query.delete()

        """create user dic_obj to use for tests"""
        self.user = {'username':'test', 'full_name':'test name', 'password': 'test_password'}
        self.count = 0
        

    def tearDown(self):
        """clean up any fouled transaction."""

        db.session.rollback()

    #===============================================================================================================================================================

    def test_create_user_obj_try_login(self):
        """test creates user and try to login"""


        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            client.post('/login')
            user = User.authenticate(username=self.user['username'], pwd=self.user['password'])

            #make sure the password is hashed and is not the same as the user's password in the dictionar obj
            self.assertNotEqual(self.user['password'], user.password)

            #make sure that the user name is matched with user name in the dictionar object
            self.assertEqual(self.user['full_name'], user.full_name)


            #try to log in using the wrong password
            user = User.authenticate(username=self.user['username'], pwd='wrong_password')

            self.assertEqual(user, False)


    #================================================================================================================================================================


    def test_create_recover_password_pin(self):
        """the test generates a PIN to recover the password"""

        pin = ''.join(sample("0123456789", 8))

        pin_obj = RecoverPassword(pin=pin, username=self.user['username'])
        db.session.add(pin_obj)
        db.session.commit()

        self.assertEqual(len(str(pin_obj.pin)), len(pin))
        self.assertEqual(pin_obj.pin, int(pin))
        self.assertEqual(pin_obj.username, self.user['username'])



    #===============================================================================================================================================================


    def test_create_salt_for_password(self):
        """test the salt creation and check if it matches"""

        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            salt = Salt.query.filter_by(user_id=user.id).first()

            #make sure that the user salt is matched with salt from table Salt
            self.assertEqual(user.salt[0].value, salt.value)

    #============================================================================================================================================================

    def test_img_creae_obj(self):
        """test create image object in database"""

        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            #simulate image content
            SMALLEST_JPEG_B64 = """
                                /9j/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8Q
                                EBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k=
                                """
            #creating simulate image in file storage object FileStorage (as used by Flask under the hood).
            image = FileStorage(stream=io.BytesIO(base64.b64decode(SMALLEST_JPEG_B64)), filename="example image.jpg", content_type="image/jpg",)

            #creae image in database
            img_obj = Img.save_img(user_id=user.id, image=image.read())

            #make sure that the image matches with a user image
            self.assertEqual(img_obj.image, user.img[0].image)


    #=============================================================================================================================================================


    def test_create_email_for_user_in_db(self):
        """test create email object in database"""


        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            #need to simulate code validation before creating email object
            pin = ''.join(sample("0123456789", 4))

            email_obj = userEmail(user_id=user.id, email='test@email.com', code_verified=pin)
            db.session.add(email_obj)
            db.session.commit()

            #make sure that the email matches with a user email
            self.assertEqual(email_obj.email, user.email[0].email)

            self.assertEqual(int(email_obj.code_verified), int(pin))

            #email not yet verified
            self.assertEqual(email_obj.verified, False)


    #=============================================================================================================================================================

    def test_create_phone_number_for_user_in_db(self):
        """test create email object in database"""


        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            #insert into providers table a provider networks in the US
            verizon = Provider(name='Verizon', value='@vtext.com')

            db.session.add(verizon)
            db.session.commit()

            #need to simulate code validation before creating phone number object
            pin = ''.join(sample("0123456789", 4))

            num_obj = userPhone(user_id=user.id, number='8888888888', provider=verizon.id, code_verified=pin)
            db.session.add(num_obj)
            db.session.commit()

            #make sure that the phone matches with a user phone number
            self.assertEqual(num_obj.number, user.phone[0].number)

            self.assertEqual(int(num_obj.code_verified), int(pin))

            #phone not yet verified
            self.assertEqual(num_obj.verified, False)


    #=============================================================================================================================================================

    def test_create_user_coins_set(self):
        """test create coins objects in database"""


        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            #creating six coins in the table related to the current user
            coin_1 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='BTC')
            coin_2 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='ETH')
            coin_3 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='XRP')
            coin_4 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='BCH')
            coin_5 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='LTC')
            coin_6 = UserCoinsForFrontEnd(user_id=user.id, coin_symbol='WBTC')

            db.session.add_all([coin_1,coin_2,coin_3,coin_4,coin_5,coin_6])
            db.session.commit()


            #get all coins by user id
            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            #make sure 6 coins were created in the database belonging to the current user
            self.assertEqual(len(coins),6)


    #=============================================================================================================================================================

    def test_create_user_tracing_coins_set(self):
        """test create coins objects in database"""


        #it is necessary to activate the HTTP request because in the User model we are using the session object
        with app.test_client() as client:

            client.post('/signup')
            user = User.register(username=self.user['username'], full_name=self.user['full_name'], password=self.user['password'])

            #creating six coins in the table related to the current user
            coin_1 = TrackingCoins(user_id=user.id, coin_symbol='BTC', user_rate='3000', by_email='on', by_phone='on', goes='up')
            coin_2 = TrackingCoins(user_id=user.id, coin_symbol='ETH', user_rate='3000', by_email='on', by_phone='on', goes='up')
            coin_3 = TrackingCoins(user_id=user.id, coin_symbol='XRP', user_rate='3000', by_email='on', by_phone='on', goes='up')
            coin_4 = TrackingCoins(user_id=user.id, coin_symbol='BCH', user_rate='3000', by_email='on', by_phone='on', goes='up')
            coin_5 = TrackingCoins(user_id=user.id, coin_symbol='LTC', user_rate='3000', by_email='on', by_phone='on', goes='up')
            coin_6 = TrackingCoins(user_id=user.id, coin_symbol='WBTC', user_rate='3000', by_email='on', by_phone='on', goes='up')

            db.session.add_all([coin_1,coin_2,coin_3,coin_4,coin_5,coin_6])
            db.session.commit()

            tracking_coins = TrackingCoins.query.filter_by(user_id=user.id).all()


            #get all coin symbols as a list throw user object
            user_coins_symbols = [coin.coin_symbol for coin in user.tracking_coins]

            #make sure 6 coins were created in the database belonging to the current user
            self.assertEqual(len(user_coins_symbols),len(tracking_coins))

            #the loop will check that all coins are presented in the returned data for the user
            for coin in tracking_coins:

                #check the user email tracking option is terned on
                self.assertEqual(coin.by_email, 'on')

                #check that the returned coin symbol is in the user's default coin set
                self.assertIn(coin.coin_symbol, user_coins_symbols)




