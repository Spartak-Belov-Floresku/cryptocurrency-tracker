from flask import Flask, render_template, redirect, flash, session, g, jsonify, request, Response
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
import json
from apscheduler.schedulers.background import BackgroundScheduler

from models import *
from forms import LoginForm, RegisterUserForm, SettingsForm, RecoverPassword

from helper import UserSession
from email_sender import sendEmailApp
from tracking_server import activateTracking
  


PUBLIC_ID = "public_id"

app = Flask(__name__)
CSRFProtect(app) #using for ajax CSRF token


app.config.from_object('config.Config')
toolbar = DebugToolbarExtension(app)

connect_db(app)

#the helper class for communications between server and user
user_session = UserSession(PUBLIC_ID)



"""
setup methods to run every 30 seconds to check the pins of the users 
with coins prices and sends notification to the users if the pins are matched 
"""
def running_tracking_server():
    """
    this method will run an independent form application. 
    Every 60 seconds it will call a class that will check user's rates for cryptocurrencies. 
    If rates will match, the user will get notification
    """
    activate_tracking = activateTracking()
    activate_tracking.strat_to_check()

#coalescing turned off for new jobs by default
#a default maximum instance limit of 3 for new jobs
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

#setup jod to run method running_tracking_server every 30 seconds
@app.before_first_request
def before_first_request():
    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    scheduler.add_job(running_tracking_server, 'interval', seconds=60)
    scheduler.start() 



@app.before_request
def add_user_to_g():
    """If user is logged in, add curr user globaly to the Flask"""
    user = user_session.current_user()

    if user:
        #assing curr user object to the global variable 
        g.user = user
        if len(g.user.img):
            g.image = user_session.decode_string_to_file(g.user.img[0].image)
    else:
        g.user = None



@app.route('/')
def home_page():
    """user home page"""

    if not g.user:
        return redirect('/login')

    #prossesing data for the user interface
    user_coins_obj, coins_data_obj = user_session.get_coins_details(g.user.id)
    return render_template('index.html', user_coins_obj=user_coins_obj, coins_data_obj=coins_data_obj)



@app.route('/api/coin/userset', methods=['POST'])
def remove_coin_from_user_set():
    """removing or adding coin inside the table that is related to the current user"""

    if not g.user:
        return jsonify({'response':False}), 401

    json_data = request.get_json(silent=True)
    action = json_data['$json']['action']
    symbol = json_data['$json']['coin_symbol'].strip()

    result = user_session.update_coins_data_for_user_db_set(g.user, symbol, action)

    return jsonify(result), 201



@app.route('/api/coins/data/update')
def send_price_data_to_ui():

    if not g.user:
        return jsonify({'response':False}), 401

    user_coins_obj, coins_data_obj = user_session.get_coins_details(g.user.id)
    return jsonify(user_coins_obj), 201




@app.route('/api/track/user/coin', methods=['POST'])
def add_user_coin_track():
    if not g.user:
        return jsonify({'response':False}), 401

    json_data = request.get_json(silent=True)

    stop_traking = json_data['json'].get('stop_tracking', None)

    #if user wants to stop tracking coin
    if stop_traking:
        resp = user_session.stop_tracking_coin(g.user.id, json_data['json'].get('coin_symbol'))
        return jsonify(resp), 201

    #setup tracking to the coin
    resp = user_session.set_up_tracking_coin(g.user, json_data)
    return jsonify(resp), 201




@app.route('/login', methods=['GET','POST'])
def login_user():
    """login user and creating session public id"""

    #if user currantly in session redirect to the user home page
    if g.user:
        return redirect('/')

    form = LoginForm()

    # checking if user submitted data to login
    if form.validate_on_submit():

        username = form.username.data.strip()
        password = form.password.data.strip()

        user = User.authenticate(username, password)

        if user:

            flash(f"Hello, {user.full_name}!", "success")
            return redirect('/')

        flash("Username or password is incorrect!", "alert alert-danger")
    
    form_name = "Log In :"
    recover_password_link = True

    return render_template('user_forms.html', form = form, form_name = form_name, recover_password_link = recover_password_link)




@app.route('/signup',methods=['GET','POST'])
def sing_up_user():
    """creating a new user and creating session public id"""

    #if user currantly in session redirect to the user home page
    if g.user:
        return redirect('/')

    form = RegisterUserForm()

    # checking if user submitted data to login
    if form.validate_on_submit():

        full_name = form.full_name.data.strip()
        username = form.username.data.strip()
        password = form.password.data.strip()

        #checking if username already exists in db
        if user_session.if_username_exists(username):

            flash(f"Username: <b>{username}</b> is already taken", "alert alert-danger")

            #redirect to singup page again
            return redirect('/signup')

        length_flag = user_session.check_length_username_and_password(username, password)
        #checking length username or password

        if length_flag:

            flash(length_flag, "alert alert-danger")
            #redirect to singup page again
            return redirect('/signup')

        user = User.register(username, full_name, password)

        if user:

            flash(f"Hello <b>{user.full_name}</b>, your account has been registred!", "alert alert-success")
            return redirect('/')

    form_name = "Register :"

    return render_template('user_forms.html', form = form, form_name = form_name)




@app.route('/recover_password', methods=['GET','POST'])
def recover_password_for_username():
    """loading recover password form"""

    if g.user:
        return redirect('/')
        
    form = RecoverPassword()

    if form.validate_on_submit():

        username = form.username.data.strip()
        code = form.code.data.strip()

        if not code:
        #check if user does not send a code, executing the first method generating code
            form.username = username
            
            form.code.render_kw = {'disabled': False, 'required': True}

            result = user_session.recover_password(username)

            flash(result , "alert alert-danger")

        if code and username:
        #if user recived the code, now the user can recover the password

            result = user_session.recover_password(username, code)

            form.code.render_kw = {'disabled': True, 'required': False}

            flash(result, "alert alert-danger")

    form_name = "Recover password :"

    return render_template('user_forms.html', form=form, form_name = form_name)



@app.route('/settings')
def settings_page():
    """user settings page"""

    if not g.user:
        return redirect('/login')

    form = SettingsForm(obj=g.user)

    providers =Provider.query.all()

    return render_template('settings.html', form=form, providers=providers)



@app.route('/logout')
def logout_user():
    """logout user"""

    user_session.do_logout()

    flash(f"You successfully logged out", "alert alert-success")
    return redirect('/login')




@app.route('/api/available/username')
def check_username():
    """checking username availability"""

    username = request.args.get('username', None)

    if username:
        username = username.strip()
    
        if user_session.if_username_exists(username): 
        # if username is already existed send notification to the user

            if not g.user or (g.user.username != username):
            # check if the user is not logged in or the curr user tries to take username that is referred to the other user

                return jsonify({'response': True}), 201

    return jsonify({'response': False}), 201




@app.route('/api/update/profile', methods=['PATCH'])
def update_user_profile():
    """change user's profile data"""

    if not g.user:
        return jsonify({'response':False}), 401
    
    url_data = request.form.get('json_data')
    json_data = json.loads(url_data)

    resp_data = {'response': False}

    #check if password and username match
    old_password = json_data['old_password'].strip()

    user = User.authenticate(g.user.username, old_password)
    # check athentication to make changes to the current account

    if not user:
        resp_data['old_password'] = 'You need your current password to make changes'

    #if user wants delete account
    if json_data.get('delete_account', None) and user:
        if user_session.delete_user_account(g.user):
            g.user = None
            g.image = None
            return jsonify({'response': True}), 201

    #check if user wants to change username
    username = json_data.get('username', None)

    if username:

        username = username.strip()

        if username != g.user.username and len(username) > 2 and user:
            #if user tries to change username to the username that is referred to the onther user

            if user_session.if_username_exists(username):
                resp_data['username'] = f'Username: {username} is already taken'
            else:
                g.user.username = username

        elif username != g.user.username and len(username) < 2 and user:

            resp_data['username'] = 'Username should have at least 2 characters'

    #check if user wants to change full name
    full_name = json_data.get('full_name', None)
    
    if full_name:
        full_name = full_name.strip()

        #checking legth of a full name
        if len(full_name) >= 2 and full_name != g.user.full_name and user:
            g.user.full_name = full_name

        elif len(full_name) < 2 and user:
            resp_data['full_name'] = 'Full name should have at least 2 characters'


    #check if user wants to change password
    new_password = json_data.get('new_password', None)

    if new_password:
        new_password = new_password.strip()

        #checking legth of a new password
        if new_password != '' and len(new_password) < 6 and user:

            resp_data['new_password'] = 'New password should have at least 6 characters'
            
        elif len(new_password) >= 6 and user:
            
            g.user.password = user_session.hashing_new_password(new_password, g.user.salt[0].value)


    #gettin image file from the user
    image = request.files.get('image', None)

    if image and user:

        #if user wants to replace old image sending a new image file to the helper to uplod to db
        flag = user_session.upload_image_to_db(g.user, image)

        #if user sends not image file server will notify the user
        if not flag:
            resp_data['image'] ='Image should be jpg, jpeg, or png'

    # checking if not errors save new data for the curr user
    if len(resp_data) == 1:
       resp_data = {'response': True}
       User.save_updated_data(g.user)

    return jsonify(resp_data), 201



@app.route('/api/request/confirm/email', methods=['POST'])
def inser_email_send_code():
    """
    mMthod will insert email into db and send code varification to the email.
    Also confirm that the email belongs to the user.
    """

    if not g.user:
        return jsonify({'response':False}), 401

    #getting user data 
    json_data = request.get_json(silent=True)
    email_id = json_data['json'].get('email', None)
    code_email = json_data['json'].get('code', None)

    #creating pin code to verification of user email
    pin = user_session.generate_pin(4)

    #running code to insert a new email and pin code into db and send the pin code to the user
    if not code_email:

        email_id = email_id.strip()

        user_email_obj = userEmail.query.filter_by(user_id=g.user.id).first()
        email_obj = userEmail.query.filter_by(email=email_id).first()

        #check if the email id exists in the db and is associated with another user
        if email_obj:
            if email_obj.user_id != g.user.id:
                return jsonify({'email': False, 'message': 'You cannot use that email because it is related to another user.'}), 201

        if not user_email_obj:
            #create a new eamil in db
            user_email_obj = userEmail(user_id=g.user.id, email=email_id, code_verified=pin)
        else:
            #update user email to a new email id
            user_email_obj.email = email_id
            user_email_obj.code_verified = pin
            user_email_obj.verified = False

        db.session.add(user_email_obj)
        db.session.commit()

        result = False

        #send pin to the user email
        send_email = sendEmailApp(email_id, 'Code verification.')
        result = send_email.formation_request(pin)

        #if email was not sent the pin varification, notify user
        if not result:
            return jsonify({'email': False, 'message': 'The PIN was not sent. Please try again later.'}), 201

        #send responce that the pin code has been send to the user email
        return jsonify({'email': True, 'message': f'PIN has been sent to email: <b>{email_id}</b>. Please allow 10 minutes, <b>do not reload the page</b>'}), 201

    #running code to verify pin with the pin that in database and activation of the user email
    else:

        code_email = code_email.strip()

        user_email_obj = userEmail.query.filter_by(user_id=g.user.id).first()

        #checking if user has email in database
        if not user_email_obj or not user_email_obj.email == email_id:
            #if user does not have email into data base or user email does not match
            return jsonify({'code': True,'message': f'Email: {email_id} does not exist in db.'}), 201

        #checking if provided pin code matches with the pin code in db
        if not code_email == user_email_obj.code_verified:
            #if code provided by the user is not matched with the code in db
            return jsonify({'code': True, 'message': f'PIN: {code_email} does not match.'}), 201

        #final running to activate a user email
        user_email_obj.verified = True

        db.session.add(user_email_obj)
        db.session.commit()

        #send success to the user
        return jsonify({'code': False, 'message': f'You have successfully activated your email: <b>{email_id}</b>'}), 201
        



@app.route('/api/request/confirm/phone', methods=['POST'])
def inser_phone_send_code():
    """method will insert phone into db and send code to the phone number"""

    if not g.user:
        return jsonify({'response':False}), 401

    #getting user data 
    json_data = request.get_json(silent=True)
    provider_id = json_data['json'].get('provider', None)
    phone_number = json_data['json'].get('phone', None)
    code_phone = json_data['json'].get('code', None)

    #remove hyphens from user number
    phone_number = phone_number.replace('-','').strip()

    #creating pin code to verification of user phone number
    pin = user_session.generate_pin(4)

    #running code to insert a new phone number and pin code into db and send the pin code to the user
    if not code_phone:

        provider = Provider.query.filter_by(id=provider_id).first()

        if not provider:
            #if user tries to manipulate with data
            return jsonify({'phone': False, 'message': 'Unfortunately, this provider is not in the database.'}), 201

        user_phone_obj = userPhone.query.filter_by(user_id=g.user.id).first()
        phone_obj = userPhone.query.filter_by(number=phone_number).first()

        #check if the phone number id exists in the db and is associated with another user
        if phone_obj:
            if phone_obj.user_id != g.user.id:
                return jsonify({'phone': False, 'message': 'You cannot use that phone because it is related to another user.'}), 201

        if not user_phone_obj:
            #create a new phone number in db
            user_phone_obj = userPhone(user_id=g.user.id, number=phone_number, provider=provider_id, code_verified=pin)
        else:
            #update user phone number to a new phone number
            user_phone_obj.number = phone_number
            user_phone_obj.provider = provider_id
            user_phone_obj.code_verified = pin
            user_phone_obj.verified = False

        db.session.add(user_phone_obj)
        db.session.commit()
        
        #formation number before to send code 
        phone_number_formated = phone_number+provider.value 


        result = False

        #send pin to the user phone number
        send_email = sendEmailApp(phone_number_formated, 'Code verification.')
        result = send_email.formation_request(pin)

        #if text message was not sent the pin varification, notify user
        if not result:
            return jsonify({'phone': False, 'message': 'The PIN was not sent. Please try again later.'}), 201

        #send responce that the pin code has been send to the user phone number
        return jsonify({'phone': True, 'message': f'PIN has been sent to phone: <b>{phone_number}</b>. Please allow 10 minutes, <b>do not reload the page</b>'}), 201

    #running code to verify pin with the pin that is in database and also activation of the user phone number
    else:

        code_phone = code_phone.strip()

        user_phone_obj = userPhone.query.filter_by(user_id=g.user.id).first()

        #checking if user has phone number in database
        if not user_phone_obj or not user_phone_obj.number == phone_number:
            #if user does not have phone number into data base or user phone number does not match
            return jsonify({'code': True,'message': f'Number: {phone_number} does not exist in db.'}), 201

        #checking if provided pin code matches with the pin code in db
        if not code_phone == user_phone_obj.code_verified:
            #if code provided by the user is not matched with the code in db
            return jsonify({'code': True, 'message': f'PIN: {code_phone} does not match.'}), 201

        #final running to activate a user email
        user_phone_obj.verified = True

        db.session.add(user_phone_obj)
        db.session.commit()

        #send success to the user
        return jsonify({'code': False, 'message': f'You have successfully activated your phone number: <b>{phone_number}</b>'}), 201




"""process a bad http request displaying a 404 error page"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
