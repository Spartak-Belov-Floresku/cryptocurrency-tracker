from threading import Thread
import requests
import json
from decimal import Decimal, ROUND_HALF_UP

from email_sender import sendEmailApp
from models import db, User, userEmail, userPhone, Provider, TrackingCoins


"""
reduce queuing time with multithreading classes
checkUserRates and notifyUser
"""


class activateTracking:
    """
    This class will get two different types of up and down tracking options from database.
    The class also will create dictionary that will contain later data on the cryptocurrency rates.
    The class will then run two different threads that will test users requests for the price.
    """

    def __init__(self):

        #geting data from database
        self.user_tracking_up = TrackingCoins.query.filter_by(goes='up').all()
        self.user_tracking_down = TrackingCoins.query.filter_by(goes='down').all()

        self.coins_dic = self.get_coins_from_server()
    
    def get_coins_from_server(self):

        #getting crypto_coins data from coincap server
        resp = requests.get('https://api.coincap.io/v2/assets')

        #convert to JSON obj
        coins = json.loads(resp.text)

        #dictionary that will contain symbol coin as the key and rate as a value
        coins_dic = {}

        for coin in coins['data']:
            coin_price = 0.00
            if coin['priceUsd']:
                coin_price =  Decimal(coin['priceUsd']).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            
            coins_dic[coin['symbol']] = coin_price

        return coins_dic

    def strat_to_check(self):
        #runs two diffrent threads up and down

        thread_1 = checkUsersRates(self.user_tracking_up, self.coins_dic, 'up')
        thread_2 = checkUsersRates(self.user_tracking_down, self.coins_dic, 'down')
        thread_1.start()
        thread_2.start()


class checkUsersRates(Thread):
    """class will check user's coin rate and format the new thread to send notification to the user"""

    def __init__(self, user_tracking_coins, server_coins, way):
        Thread.__init__(self)
        self.user_tracking_coins = user_tracking_coins
        self.server_coins = server_coins
        self.way = way


    def run(self):
        #superclass inheritance method that activates a new thread when this method is called

        self.start_to_check_rates()

    
    def start_to_check_rates(self):

        for user_coin in self.user_tracking_coins:
            current_rate = self.server_coins[user_coin.coin_symbol]

            if current_rate > float(user_coin.user_rate) and self.way == 'up':
                # if rate raises and exceeded user rate, notify the user by creating a new thread

                thread_up = notifyUser(user_coin, current_rate)
                thread_up.start()


            elif current_rate < float(user_coin.user_rate) and self.way == 'down':
                # if rate drops below the user's rate, notify the user by creating a new thread

                thread_down = notifyUser(user_coin, current_rate)
                thread_down.start()


class notifyUser(Thread):

    def __init__(self, user_coin, current_rate):
        Thread.__init__(self)
        self.user_id = user_coin.user_id
        self.coin_symbol = user_coin.coin_symbol
        self.by_email = user_coin.by_email
        self.by_phone = user_coin.by_phone
        self.current_rate = current_rate


    def run(self):
        #superclass inheritance method that activates a new thread when this method is called

        self.send_email_phone_notification()


    def send_email_phone_notification(self):
        """user will receive notification in the way the user prefers"""

        if self.by_email == 'on':
            user_email = userEmail.query.filter_by(user_id=self.user_id).first()
            if user_email:
                #send current rate of cryptocoin to the user email

                send_note = sendEmailApp(user_email.email, f'Current rate {self.coin_symbol}')
                send_note.formation_request(f'{self.coin_symbol} '+'${:,.2f}'.format(self.current_rate))
        
        if self.by_phone == 'on':
            user_phone = userPhone.query.filter_by(user_id=self.user_id).first()
            provider = Provider.query.filter_by(id=user_phone.provider).first()

            if user_phone:

                #formation number before to send coin's rate
                phone_number_formated = user_phone.number+provider.value 

                #send current rate of cryptocoin to the user phone
                
                send_note = sendEmailApp(phone_number_formated, 'Current rate ')
                send_note.formation_request(f'{self.coin_symbol} is '+'${:,.2f}'.format(self.current_rate))

