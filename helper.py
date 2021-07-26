from flask import session, redirect
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from base64 import b64encode
from random import sample
import json
import requests
from os.path import isfile
from decimal import Decimal, ROUND_HALF_UP



from models import db, User, RecoverPassword, Salt, Img, userEmail, userPhone, UserCoinsForFrontEnd, TrackingCoins
from email_sender import sendEmailApp


bcrypt = Bcrypt()



IMG_PATH = 'static/img/icons/'


class UserSession:
    """helper calss to manipulate with user data"""

    def __init__(self, public_id):
        self.public_id = public_id


    
    def current_user(self):
        """check if current user loged in"""

        if self.public_id in session:

            #check if public_id exists in db
            user = User.query.filter_by(public_id=session[self.public_id]).first()

            if user:
                return user

            else:
                #if user public id does not exist, remove current session
                del session[self.public_id]
                session.pop('_flashes', None)
                return False

        else:
            return False


    
    def decode_string_to_file(self, img_str):
        """decode string from database"""

        return b64encode(img_str).decode("utf-8")


    def recover_password(self, username, code=None):
        """this method helps to the user to recover forgoten password"""

        #trying to get user by username
        user = self.if_username_exists(username)

        if not code and user:

            #if user exists generate pin code that will send to the user contacts to recover the password 
            pin = self.generate_pin(8)

            send_method = False

            #use available way to send pin to the user
            if user.email:
                if user.email[0].verified:
                    send_method = user.email[0].email


            if user.phone and not send_method:
                if user.phone[0].verified:
                    send_method = user.phone[0].number


            if send_method:
                #save pin with username to the database and send pin to the user

                try:
                    #if user try to insert into database the same username two times this block prevents crash
                    recover_pin = RecoverPassword(pin=pin, username=username)
                    db.session.add(recover_pin)
                    db.session.commit()

                except:
                    db.session.rollback()
                    try:
                        RecoverPassword.query.filter_by(username=username).delete()
                        db.session.commit()
                    except:
                        try:
                            RecoverPassword.query.filter_by(pin=code).delete()
                            db.session.commit()
                        except:
                            pass

                    return "Something wrong, please try again later!"

                    

                send_email = sendEmailApp(send_method, 'Code verification to recover password.')
                send_email.formation_request(f'If you have not submitted request to change your password, please ignore this message. Your pin {pin}')

                return f"Recover code was sent to the email or phone that are associated with username: <b>{username}</b>"
        

        elif code and user:
            # if code and the username were sent to recover password

            result = None

            try:
                #try to avoid db crash if data was provided incorrectly
                result = RecoverPassword.query.filter_by(pin=code, username=user.username).first()

            except:
                try:
                    RecoverPassword.query.filter_by(username=username).delete()
                    db.session.commit()
                except:
                    try:
                        RecoverPassword.query.filter_by(pin=code).delete()
                        db.session.commit()
                    except:
                        pass
                pass

            if result:
                #generate a temporary new password
                new_password = self.generate_pin(8)

                salt = user.salt[0].value

                #salted a new temporary password before send to the database
                user.password = self.hashing_new_password(new_password, salt)
                send_method = False

                #use available way to send pin to the user
                if user.email:
                    if user.email[0].verified:
                        send_method = user.email[0].email


                if user.phone and not send_method:
                    if user.phone[0].verified:
                        send_method = user.phone[0].number

                if send_method:
                    #send a new password to the user
                    send_email = sendEmailApp(send_method, 'Temporary password.')
                    send_email.formation_request(new_password)

                    RecoverPassword.query.filter_by(username=user.username).delete()
                    db.session.commit()

                #save a new password for the user
                User.save_updated_data(user)

                return "New password was sent"

        
        #if someone tries to hijack an account, remove object by username or pin from recover table
        try:
            RecoverPassword.query.filter_by(username=username).delete()
            db.session.commit()
        except:
            try:     
                RecoverPassword.query.filter_by(pin=code).delete()
                db.session.commit()
            except:
                pass


        return "Something wrong, please try again later!"
        
            

    def do_logout(self):
        """Logout user."""

        if self.public_id in session:

            del session[self.public_id]
            # also clear all falsh messages

            session.pop('_flashes', None)




    def if_username_exists(self, username):
        """running method to check if username already exists"""

        user = User.query.filter_by(username=username).first()

        return user




    def check_length_username_and_password(self, username, password):
        """checking length username and password to validate for db"""

        if len(username) < 2:
            return 'Username should have at least two characters'
        if len(password) < 6:
            return 'Password should have at least six characters'

        return False



    def upload_image_to_db(self, user, image):
        """method stores image into db"""

        extension = ['image/jpg', 'image/jpeg', 'image/png']

        img_type = image.mimetype

        #if file is not image return false
        if not img_type in extension:
            return False

        image = Img.save_img(user_id=user.id, image=image.read())

        if not image:
            return False

        return image



    def hashing_new_password(self, password, salt):
        """create a new password for user"""

        #add solt to the new password
        salted_password = salt+password

        password_hash = bcrypt.generate_password_hash(salted_password)

        # turn bytestring into normal (unicode utf8) str
        return password_hash.decode("utf8")


    def delete_user_account(self, user):
        """method will complitly remove all user data from database"""

        try:
            Salt.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            Img.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            userEmail.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            userPhone.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            UserCoinsForFrontEnd.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            TrackingCoins.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            User.query.filter_by(id=user.id).delete()
            db.session.commit()

            return True
        except:
            return False

    def generate_pin(self, count):
        """method is going to generate digits number for confirmation user's email or phone"""

        return ''.join(sample("0123456789", count))



    def get_coins_details(self, user_id):
        """running - receiving and processing data from a remote server"""

        #getting crypto_coins data from coincap server
        resp = requests.get('https://api.coincap.io/v2/assets')

        #convert to JSON obj
        coins = json.loads(resp.text)
        coins_list = []

        #getting user has preferable coins
        user_coins_symbols = self.get_user_coins_front_end(user_id)

        user_coins = []

        #getting coins that the user currently tracks
        user_tracking_coins, user_tracking_symbol_coins = self.getting_tracking_coins_by_user_id(user_id)



        for coin in coins['data']:
        #running loop to extract necessary data from JSON obj

            coin_price = 0.00
            if coin['priceUsd']:
                coin_price =  Decimal(coin['priceUsd']).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

            if coin_price >= 0.01:
                coin_symbol = coin['symbol']
                path_img_coin  = f'{IMG_PATH}{coin_symbol.lower()}.png'

                coin_name = coin['name']
                coin_explorer = coin['explorer']
                coin_change_price = 0.00

                if coin['changePercent24Hr']:
                    coin_change_price =  Decimal(coin['changePercent24Hr']).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

                coin_img = ''
                
                #running check if image exists for the coin
                if isfile(path_img_coin):
                    coin_img = path_img_coin
                else:
                    #if not addpath to the default img
                    coin_img = f'{IMG_PATH}default.png'
                

                if coin_symbol in user_coins_symbols:
                    obj = ''
                    if coin_symbol in user_tracking_symbol_coins:
                        for user_tracking_coin in user_tracking_coins:
                            if user_tracking_coin.coin_symbol == coin_symbol:
                                #create JSON object that holds all parameters for tracking coins
                                obj = {
                                        'coin_img': coin_img, 
                                        'coin_symbol': coin_symbol, 
                                        'coin_price': '${:,.2f}'.format(coin_price), 
                                        'coin_change_price': '{:,.1f}'.format(coin_change_price)+'%',
                                        'coin_name': coin_name, 
                                        'coin_explorer': coin_explorer, 
                                        'rank': coin['rank'],
                                        'track_input': True,
                                        'track_rate': user_tracking_coin.user_rate,
                                        'track_email': user_tracking_coin.by_email,
                                        'track_phone': user_tracking_coin.by_phone,
                                        'track_goes': user_tracking_coin.goes
                                        }
                    else:
                        #create JSON object that holds all parameters for the coins in the user set
                        obj = {
                                'coin_img': coin_img, 
                                'coin_symbol': coin_symbol, 
                                'coin_price': '${:,.2f}'.format(coin_price), 
                                'coin_change_price': '{:,.1f}'.format(coin_change_price)+'%',
                                'coin_name': coin_name, 
                                'coin_explorer': coin_explorer, 
                                'rank':coin['rank'],
                                'track_input': False,
                                'track_rate': False,
                                'track_email': False,
                                'track_phone': False,
                                'track_goes': False
                                }

                    user_coins.append(obj)
                else:
                    #append available coins for a user's choose
                    coins_list.append({
                                        'coin_img': coin_img, 
                                        'coin_symbol': coin_symbol, 
                                        'coin_price': '${:,.2f}'.format(coin_price), 
                                        'coin_change_price':'{:,.1f}'.format(coin_change_price)+'%',
                                        'coin_name': coin_name, 
                                        'coin_explorer': coin_explorer, 
                                        'rank':coin['rank']
                                    })

        return user_coins, coins_list



    def get_user_coins_front_end(self, user_id):
        """checking if user has preferable coins"""

        coins = UserCoinsForFrontEnd.query.filter_by(user_id=user_id).all()
        user_coins_symbol = []

        if len(coins):
            user_coins_symbol = [coin.coin_symbol for coin in coins]
        else:
            #if user does not have preferable coins, creating default set and send it to the UI
            coin_1 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='BTC')
            coin_2 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='ETH')
            coin_3 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='XRP')
            coin_4 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='BCH')
            coin_5 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='LTC')
            coin_6 = UserCoinsForFrontEnd(user_id=user_id, coin_symbol='WBTC')
            db.session.add_all([coin_1,coin_2,coin_3,coin_4,coin_5,coin_6])
            db.session.commit()
            coins = UserCoinsForFrontEnd.query.filter_by(user_id=user_id).all()
            user_coins_symbol = [coin.coin_symbol for coin in coins]

        return user_coins_symbol



    def update_coins_data_for_user_db_set(self, user, symbol, action):
        """updated coins data for the user and the user interface"""

        #if user asks to remove coin from user set
        if action == 'DELETE':
            try:
                UserCoinsForFrontEnd.query.filter_by(user_id=user.id, coin_symbol=symbol).delete()
                db.session.commit()

                #also if user has this coin in tracking table, it will delete the coin there
                self.stop_tracking_coin(user.id, symbol)

                return {'response': True}
            except Exception as e:
                print(e)
                return {'response': False}
        

        #if user wants to add coin to the tracking system
        coin = UserCoinsForFrontEnd(user_id=user.id, coin_symbol=symbol)
        db.session.add(coin)
        db.session.commit()

        #checking if user has activated email or phone number
        user_email = {'status': False, 'email': False}

        if user.email:
            user_email['status'] = True
            if user.email[0].verified:
                user_email['email'] = user.email[0].email

        user_phone = {'status':False, 'phone': False}

        if user.phone:
            user_phone['status'] = True
            if user.phone[0].verified:
                user_phone['phone'] = user.phone[0].number


        user_coins, coins_list = self.get_coins_details(user.id)
        coin_data = {} 

        #will build and send to the ui a tracking form with the details of the coin
        for user_coin in user_coins:
            if user_coin['coin_symbol'] == symbol:
                coin_data = user_coin
                form = self.generate_tracking_form(coin_data, user_email, user_phone)
                return {'response':True, 'form': form}

        #if something wrong with user request, default response
        return {'response': False}



    def generate_tracking_form(self, user_coin, user_email, user_phone):
        """this method builds a tracking form and integries the data into the form"""

        form =  f'<div class="container mt-5 mr-1 d-flex justify-content-center coin-div" id="{user_coin["coin_symbol"]}">'
        form += f'<span class="remove-coin btn-close" data-symbol-remove="{user_coin["coin_symbol"]}"></span>'
        form += f'<div class="card p-3"><div class="d-flex align-items-center"><div class="image"><a href="{user_coin["coin_explorer"]}"><img src="{user_coin["coin_img"]}" class="rounded"></a> </div>'
        form += f'<div class="ml-3 name_symbol"><h4 class="mb-0 mt-0">{user_coin["coin_symbol"]}</h4><span>{user_coin["coin_name"]}</span></div><div class="data-info">'
        form += f'<div class="p-2 mt-2 bg-primary d-flex justify-content-between rounded text-white stats"><div class="d-flex flex-column"> <span class="articles">Price</span> <span class="number1" id="price_{user_coin["coin_symbol"]}">{user_coin["coin_price"]}</span></div><div class="d-flex flex-column"><span class="followers">24 hours</span>'
        if '-' in user_coin['coin_change_price']:
            form += f'<span class="number2 coin_change_price_red" id="coin_change_price_{user_coin["coin_symbol"]}">'
        else:
            form += f'<span class="number2 coin_change_price_green" id="coin_change_price_{user_coin["coin_symbol"]}">'
        form += f'{user_coin["coin_change_price"]}</span></div>'
        form += f'<div class="d-flex flex-column"> <span class="rating">Rank</span> <span class="number3">{user_coin["rank"]}</span></div></div></div></div></div>'
        if user_email['status'] or user_phone['status']:
            form += '<div class="tracking_forms"><h4>Tracking options by:</h4><form class="track_options">'
            form += f'<input type="hidden" name="coin_symbol" value="{user_coin["coin_symbol"]}">'
            if user_email["email"]:
                form += f'<div class="form-check form-switch"><input class="form-check-input" type="checkbox" id="by_email" name="by_email"><label class="form-check-label" for="by_email"><b>{user_email["email"]}</b></label></div>'
            if user_phone["phone"]:
                form += f'<div class="form-check form-switch"><input class="form-check-input" type="checkbox" id="by_phone" name="by_phone"><label class="form-check-label" for="by_phone"><b>{user_phone["phone"]}</b></label></div>'
            form += '<div class="input-group mb-3"><span class="input-group-text">$</span><input type="number" class="form-control" name="user_rate" aria-label="Amount (to the nearest dollar)" required></div>'
            form += '<div class="form-check form-check-inline"><input class="form-check-input" type="radio" name="goes" id="up" value="up"><label class="form-check-label" for="up">Up</label></div>'
            form += '<div class="form-check form-check-inline"><input class="form-check-input" type="radio" name="goes" id="down" value="down"><label class="form-check-label" for="down">Down</label></div>'
            form += '<div class="btn-group" role="group"><input type="submit" class="btn btn-primary tracking_btn" value="Start tracking"><input type="submit" class="btn btn-primary tracking_btn deactivated" value="Stop tracking"></div></form></div></div>'

        return form


    def set_up_tracking_coin(self, user, json_data):
        """add coin to the tracking table"""

        coin_symbol = json_data['json'].get('coin_symbol', None)
        user_rate = json_data['json'].get('user_rate', None)
        by_email = json_data['json'].get('by_email', None)
        by_phone = json_data['json'].get('by_phone', None)
        goes = json_data['json'].get('goes', None)

        #checking if user forced request without nessasary parameters
        if not user_rate or not goes or (not by_email and not by_phone): 
            return {'response': True, 'tracking': False}

        user_rate =  Decimal(user_rate).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

        track_coin = TrackingCoins(user_id=user.id, coin_symbol=coin_symbol, user_rate=user_rate, by_email=by_email, by_phone=by_phone, goes=goes)
        db.session.add(track_coin)
        db.session.commit()

        return {'response': True, 'tracking': True}


    def stop_tracking_coin(self, user_id, symbol):
        """remove coin from tracking table"""

        TrackingCoins.query.filter_by(user_id=user_id, coin_symbol=symbol).delete()
        db.session.commit()

        return {'response': True, 'tracking': False}


    def getting_tracking_coins_by_user_id(self, id):
        """get tracking coins from table"""

        tracking_coins = TrackingCoins.query.filter_by(user_id=id).all()
        symbols = []

        #creating list of symbols tracking coins
        if len(tracking_coins):
            symbols = [coin.coin_symbol for coin in  tracking_coins]

        return tracking_coins, symbols
