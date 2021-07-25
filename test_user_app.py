"""User front and back end tests."""

from unittest import TestCase
import json
import io

from app import app
from models import db, User, RecoverPassword, Salt, Img, userEmail, userPhone, Provider, UserCoinsForFrontEnd, TrackingCoins


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_tracker'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False


db.drop_all()
db.create_all()


class UserFrontAndBackTestCase(TestCase):
    """test app user view"""

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
        self.user = {'username':'test', 'full_name':'test name', 'password': 'password'}
        

    def tearDown(self):
        """clean up any fouled transaction."""

        db.session.rollback()

    #===============================================================================================================================================================

    def test_register_user_rederaction_home_page(self):
        """
        Testing user registration and home page redirection.
        The content home page should have default coins set for a new user and also the user's data
        """

        with app.test_client() as client:

            response = client.post('/signup', data=self.user, follow_redirects=True)

            html = response.get_data(as_text=True)

            #checking if user interface has user full name and BITcoin
            self.assertEqual(response.status_code, 200)
            self.assertIn(self.user['full_name'], html)
            self.assertIn('BTC', html)


    #================================================================================================================================================================

    def test_login_user_interface_home_page(self):
        """testing to logged user in, and front user interface for data"""

        #before testing the login functionality, need to create user obj in the table
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)


        #here running test to try logging user in, and the user interface should show default set of coins [BTC, ETH, XRP, BCH, LTC, WBTC]
        with app.test_client() as client:

            response = client.post('/login', data=self.user, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(self.user['full_name'], html)
            self.assertIn('BTC', html)


    #================================================================================================================================================================

    def test_login_user_incorrect_password(self):
        """testing to logged user in, trying to provide bad password"""

        #before testing the login functionality, need to create user obj in the table
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

        #change password for the user
        self.user['password'] = 'my new password'

        #here running test to try loging user in
        with app.test_client() as client:

            response = client.post('/login', data=self.user, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Username or password is incorrect!', html)
            

    #=================================================================================================================================================================

    def test_username_availability(self):
        """running test to check if the username is not in the database and the username is available"""

        #before testing the username availability, need to create user obj in the table, and logged the user out from the app
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

            client.get('/logout', follow_redirects=True)

        #testing if username is available
        with app.test_client() as client:

            resp = client.get('/api/available/username', query_string={'username':'new_test_username'})

            data = resp.json

            #checking if response False shows that the username does not exist
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(False, data['response'])


        #testing if username is not available
        with app.test_client() as client:

            username = self.user['username']
            resp = client.get('/api/available/username', query_string={'username': username})

            data = resp.json

            #checking that the answer is True shows that the username exists and is not available for the new subscriber
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(True, data['response'])


    #=================================================================================================================================================================

    def test_change_user_settings_login_again_try_upload_not_img_file(self):
        """
        running test to change username and password relogin with new username and new password.
        also try uploading non-image file
        """

        #before testing need to create user obj in the table, also loged user in, and change user data 
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)
            dic_data = {}

            #testing change user data
            dic_data['json_data'] = json.dumps({'username': 'new_username', 'new_password': 'new_password', 'old_password': self.user["password"], 'full_name': self.user["full_name"], })
            
            #try uploading new image with correct extension
            dic_data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')

            resp = client.patch("/api/update/profile", data=dic_data, headers={'Content-Type': 'multipart/form-data'})

            data = resp.json

            #checking if data was updated
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(True, data['response'])


        #check if after logout redirect to login page
        with app.test_client() as client:

            response = client.get('/logout', follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Log In :', html)


        #here running test to try loging user in back with updated username and password
        with app.test_client() as client:

            new_user_data = {'username':'new_username', 'password': 'new_password'}

            response = client.post('/login', data=new_user_data, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(new_user_data['username'], html)
            self.assertIn('BTC', html)


        #here running test to try uploading not image file
        with app.test_client() as client:

            #before test need to login user
            user_data = {'username':'new_username', 'password': 'new_password'}

            response = client.post('/login', data=user_data, follow_redirects=True)

            #to upload file need to provide currant password
            dic_data['json_data'] = json.dumps({'old_password': 'new_password',})
            
            #try uploading pdf file instead img file
            dic_data['image'] = (io.BytesIO(b"abcdef"), 'test.pdf')

            resp = client.patch("/api/update/profile", data=dic_data, headers={'Content-Type': 'multipart/form-data'})

            data = resp.json

            #checking if return False and note that the file is inappropriate
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(False, data['response'])
            self.assertEqual('Image should be jpg, jpeg, or png', data['image'])



    #===============================================================================================================================================================

    def test_recover_password_for_username(self):
        """the running test will try to recover the lost password and try to log in with the new password"""

        with app.test_client() as client:

            #creating a new user and authorizing a user
            client.post('/signup', data=self.user, follow_redirects=True)

            #log out user
            client.get('/logout', follow_redirects=True)

            #sending a password recovery request
            resp = client.post('/recover_password', data={'username':self.user['username']}, follow_redirects=True)

            html = resp.get_data(as_text=True)

            #checking if user interface has user full name and BITcoin
            self.assertEqual(resp.status_code, 200)
            #since the test user does not have a verified email or phone number, the server will send a notification
            self.assertIn('Something wrong, please try again later!', html)
    
    
    #================================================================================================================================================================

    def test_delete_user_data_from_db(self):
        """test will completely remove user data from the database"""

        #before testing need to create user obj in the table, also loged user in and create the default coins set for the user
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

            dic_data = {}
            dic_data['json_data'] = json.dumps({'old_password': 'password', 'delete_account': 'on'})

            resp = client.patch("/api/update/profile", data=dic_data, headers={'Content-Type': 'multipart/form-data'})

            data = resp.json

            coins =  UserCoinsForFrontEnd.query.all()
            salts = Salt.query.all()
            users = User.query.all()

            self.assertEqual(resp.status_code, 201)

            #checking the answer for a true and all user data has been removed
            self.assertEqual(True, data['response'])
            self.assertEqual(coins, [])
            self.assertEqual(salts, [])
            self.assertEqual(users, [])
            

    #=================================================================================================================================================================

    def test_manipulate_coins_user_set(self):
        """running test to remove a coin from a user set and add a coin to the user set"""

        #before testing need to create user obj in the table, also loged user in 
        #and the app will automatically create the default coins set [BTC, ETH, XRP, BCH, LTC, WBTC] for the user
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

            #checking if user has 6 coins in the user set
            user = User.query.filter_by(username=self.user['username']).first()
            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            self.assertEqual(len(coins), 6)

            #test is running here, try to remove LTC from user installed coins
            json_data = {'$json' : {'action': 'DELETE', 'coin_symbol': 'LTC'}}

            resp = client.post('/api/coin/userset', json=json_data)

            data = resp.json

            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            self.assertEqual(resp.status_code, 201)
            #shows that the coin has been removed from user set
            self.assertEqual(True, data['response'])
            #checking if user set has 5 coins
            self.assertEqual(len(coins), 5)


        #running test tries to add a new coin to the user's set
        with app.test_client() as client:

            client.post('/login', data=self.user, follow_redirects=True)

            json_data = {'$json' : {'action': 'ADD', 'coin_symbol': 'LTC'}}

            resp = client.post('/api/coin/userset', json=json_data)

            data = resp.json

            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            self.assertEqual(resp.status_code, 201)
            #shows that the coin has been added for user set
            self.assertEqual(True, data['response'])
            #shows that a new coin form has been sent to the UI
            self.assertIn('<h4 class="mb-0 mt-0">LTC</h4><span>', data['form'])
            #checking if user set has 6 coins now
            self.assertEqual(len(coins), 6)

            
    #===========================================================================================================================================================
            
    def test_get_updated_data_coins_set_ui(self):
        """running test will get udated data for user coins set"""

        #before testing need to create user obj in the table, also loged user in 
        #and the app will automatically create the default coins set [BTC, ETH, XRP, BCH, LTC, WBTC] for the user
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

            #getting defalt user coins set
            user = User.query.filter_by(username=self.user['username']).first()
            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            user_coin_symbol_set =[coin.coin_symbol for coin in coins]

            #here calls third party server to get updated data for the user set coins
            resp = client.get('/api/coins/data/update')

            data = resp.json

            self.assertEqual(resp.status_code, 201)
            #the loop will check that all coins are presented in the returned data for the user
            for coin in data:

                #check if the dollar sign is present in the coin price
                self.assertIn('$', coin['coin_price'])

                #check the user email tracking option is false for all coins
                self.assertEqual(coin['track_email'], False)

                #check that the returned coin symbol is in the user's default coin set
                self.assertIn(coin['coin_symbol'], user_coin_symbol_set)


    #===========================================================================================================================================================
            
    def test_add_user_coin_track(self):
        """running test will try to setup tracking for the user coin by email and phone"""

        #before testing need to create user obj in the table, also loged user in 
        #and the app will automatically create the default coins set [BTC, ETH, XRP, BCH, LTC, WBTC] for the user
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)

            #getting defalt user coins set
            user = User.query.filter_by(username=self.user['username']).first()
            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user.id).all()

            user_coin_symbol_set =[coin.coin_symbol for coin in coins]
            
            json_data = {'json' : {'coin_symbol': user_coin_symbol_set[0] , 'user_rate': '3555', 'by_email':'on', 'by_phone':'on', 'goes':'up'}}

            #sending json object with coin's data to set up for tracking
            resp = client.post('/api/track/user/coin', json=json_data)

            data = resp.json

            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['response'], True)
            self.assertEqual(data['tracking'], True)


    #===========================================================================================================================================================
            
    def test_inser_email_send_code(self):
        """the test that is running will try to insert the test email into the database and validate it"""

        #before testing need to create user obj in the table, also loged user in 
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)
            
            json_data = {'json' : {'email': "test@mail.com"}}

            #sending json object try to insert email into db and generate code validation
            resp = client.post('/api/request/confirm/email', json=json_data)

            data = resp.json

            #it will show that an email has been added to use and a verification code has been sent to the user's email
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['email'], True)
            self.assertIn(f'PIN has been sent to email: <b>{json_data["json"]["email"]}</b>', data['message'])


            #here the test will manually take code validation from the database and do validation a fake email 

            user_email = userEmail.query.filter_by(email=json_data["json"]["email"]).first()


            json_data = {'json' : {'email': 'test@mail.com', 'code': user_email.code_verified}}

            #sending json object try to validate email with provided code validation
            resp = client.post('/api/request/confirm/email', json=json_data)

            data = resp.json

            #it will show that an email has been verified
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['code'], False)
            self.assertIn(f'You have successfully activated your email: <b>{json_data["json"]["email"]}</b>', data['message'])

    
    #===========================================================================================================================================================
            
    def test_inser_phone_send_code(self):
        """the test that is running will try to insert the test phone number into the database and validate it"""

        #insert into providers table a provider networks in the US
        verizon = Provider(name='Verizon', value='@vtext.com')

        db.session.add(verizon)
        db.session.commit()

        #before testing need to create user obj in the table, also loged user in 
        with app.test_client() as client:

            client.post('/signup', data=self.user, follow_redirects=True)
            
            json_data = {'json' : {'phone': "8888888888", 'provider': 1}}

            #sending json object try to insert phone number into db and generate code validation
            resp = client.post('/api/request/confirm/phone', json=json_data)

            data = resp.json

            #it will show that the number has been added to use and a verification code has been sent to the user's phone as a text message
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['phone'], True)
            self.assertIn(f'PIN has been sent to phone: <b>{json_data["json"]["phone"]}</b>', data['message'])


            #here the test will manually take code validation from the database and do validation a fake phone number 

            user_phone = userPhone.query.filter_by(number=json_data["json"]["phone"]).first()


            json_data = {'json' : {'phone': '8888888888', 'code': user_phone.code_verified}}

            #sending json object try to validate phone number with provided code validation
            resp = client.post('/api/request/confirm/phone', json=json_data)

            data = resp.json

            #it will show that an user phone number has been verified
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['code'], False)
            self.assertIn(f'You have successfully activated your phone number: <b>{json_data["json"]["phone"]}</b>', data['message'])