import json
import datetime
import md5
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import session
from flask import url_for
from flask import jsonify, make_response
from flask_oauth import OAuth
import requests
#-------------------------------------------------------------------------------
#                           CONFIGURATION VARIABLES
#-------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = '596a96cc7bf9108cd896f33c44aedc8a'
app.config['SESSION_TYPE'] = 'filesystem'

app.config['FACEBOOK'] = {
    'APP_ID': '783899738441295',
    'APP_SECRET': '9b34685d0e1849d760ae1676dd895eb8'
}

GET_FACEBOOK_INFO_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=facebookinfo&identifier="
SEND_FACEBOOK_INFO_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=facebookinfo&identifier="
REMOVE_FACEBOOK_INFO_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=facebookinfo-decouple&identifier="
NEW_ORDER_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=ziporder&identifier=new"
NEW_ORDERLINE_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=ziporderline&identifier="
NEW_CUSTOMER_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=customer&identifier=new"
MODEL_PREFERENCE = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=modelpreference&identifier="
FINAL_PAYMENTS_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=zippayment&identifier="
LAYBY_PAYMENTS_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=makepartpayment&identifier="
ZIP_DECLINE_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=ziporderrejected&identifier="
RESET_REQUEST_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=forgot-password-request"
RESET_DATAGET_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=details-from-request"
GLOBAL_BASE_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/awp_syshooks"
SCHEDULE_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=schedulepayment"
#-------------------------------------------------------------------------------
#                          FACEBOOK AUTHENTICATION
#-------------------------------------------------------------------------------
oauth = OAuth()

facebook = oauth.remote_app(
    'facebook',
        base_url = 'https://graph.facebook.com/',
        request_token_url = None,
        access_token_url = '/oauth/access_token',
        authorize_url = 'https://www.facebook.com/dialog/oauth',
        consumer_key = app.config['FACEBOOK']['APP_ID'],
        consumer_secret = app.config['FACEBOOK']['APP_SECRET'],
        request_token_params = {'scope': ('email, ')}
    )
#-------------------------------------------------------------------------------
#                          FACEBOOK AUTH ROUTES
#-------------------------------------------------------------------------------
@app.route('/facebook')
def facebookGet():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route('/facebook/login')
@facebook.authorized_handler
def facebook_authorized(resp):
    import json
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description'])
    session['oauth_token'] = (resp['access_token'], '')
    session['facebook_token'] = session['oauth_token']
    me = facebook.get('/me')
    postUrl = SEND_FACEBOOK_INFO_URL + str(session['user']['token'])
    headers = {'content-type': 'application/json'}
    payload = { "facebook_email": session['user']['email'],
        "facebook_id": str(me.data['id']),
        "facebook_token": str(resp['access_token'])}
    r = requests.post(postUrl, data=json.dumps(payload), headers=headers)
    return redirect(url_for('profilePage'))

@app.route('/facebook/logout')
def facebook_remove():
    session['oauth_token'] = None
    session['facebook_token'] = None

    POST_URL = REMOVE_FACEBOOK_INFO_URL + session['user']['token']
    remove_request = requests.get(POST_URL)
    import json
    return redirect(url_for('profilePage'))

@facebook.tokengetter
def getFacebookToken():
    return session.get('facebook_token')
#-------------------------------------------------------------------------------
#                            PUBLIC ROUTES
#-------------------------------------------------------------------------------
@app.route('/products', methods = ['GET'])
def galleryPage():
    GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_List&Token=gofuckyourself'
    request = requests.post(GET_URL)
    products = json.loads(request.content)["products"]
    print products
    return render_template("sellerPublic.html", products = products)

#-------------------------------------------------------------------------------
#                            CLIENT ROUTES
#-------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def loginPage():
    """ This route handles login. Once the email and password is posted here
    it is appended to the API call REST-Customer.awp and the response is checked
    for status. The user profile information is added to the session object on
    server-side. Needed fix for the dob_zipmoney field being nested on a higher
    level. This can be directly included into the Customer object returned by
    the API call."""
    from flask import request
    if request.method == 'GET':
        try:
            error = request.args.get('error')
        except:
            error = None
        try:
            success = request.args.get('success')
        except:
            success = None
        return render_template("login.html", error = error, success = success)
    elif request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        baseUrl = GLOBAL_BASE_URL + "/REST-Customer.awp?Procedure=Customer_LogIn&User="
        loginUrl = baseUrl + email + "&Pwd=" + password
        requestWWW = requests.post(loginUrl)
        response = json.loads(requestWWW.content)
        if str(response['Status']['Successful']) == "True":
            session['user'] = response['Customer']
            session['user']['dob_zipmoney'] = response['dob_zipmoney']
            firstLogin = response['first_login']
            if request.form['wasGuest'] == "None":
                response = make_response(redirect(url_for('profilePage', ref = firstLogin)))
                response.set_cookie(b'somebody_is_logged', "True", domain=".skillion.com.au")
                return response
            else:
                paymentType, paymentToken = request.form['wasGuest'].split(":::")
                if paymentType == "outright":
                    return redirect(url_for('deliveryOutright', token = paymentToken))
                elif paymentType == "layby":
                    return redirect(url_for('deliveryLayby', token = paymentToken))
                elif paymentType == "zip":
                    return redirect(url_for('zipDelivery', token = paymentToken))
                else:
                    return render_template("error/404.html")
        else:
            return render_template("login.html", error = "Incorrect credentials")
#-------------------------------------------------------------------------------
@app.route('/logout')
def logOut():
    """ Safely deletes the session object for the user by setting it to a null
    value. This is the logout route. """
    session['user'] = ""
    response = make_response(redirect("https://skillion.com.au", code=302))
    response.set_cookie(b'somebody_is_logged', "False", domain=".skillion.com.au")
    return response
#-------------------------------------------------------------------------------
@app.route('/reset/forgot', methods=['GET', 'POST'])
def forgotPassOne():
    if request.method == "GET":
        return render_template("forgot.html")
    elif request.method == "POST":
        import json
        payload = {'email': request.form['email']}
        headers = {'content-type': 'application/json', 'x-ayfkm' : 'SOMESHIT'}
        r = requests.post(RESET_REQUEST_URL, data=json.dumps(payload),
        headers=headers)
        return redirect(url_for('loginPage', success = "Please check your email for a reset link!"))
#-------------------------------------------------------------------------------
@app.route('/user/reset/<SLOSH>', methods=['GET', 'POST'])
def masterReset(SLOSH):
    if request.method == "GET":
        return render_template("reset.html", slosh = str(SLOSH))
    elif request.method == "POST":
        import json
        payload = {}
        headers = {'content-type': 'application/json'}
        requested_payload = {"request_info": str(SLOSH)}
        r = requests.post(RESET_DATAGET_URL, data=json.dumps(requested_payload),
            headers=headers)
        old_password = json.loads(r.content)['password']
        token = json.loads(r.content)['token']

        POST_URL = MODEL_PREFERENCE + token
        payload = {}
        headers = {'content-type': 'application/json'}
        payload = {"model_preference": request.form['password'],
            "retired_model": old_password}
        r = requests.post(POST_URL, data=json.dumps(payload),
            headers=headers)
        return redirect(url_for('loginPage', success="Successfully changed password!"))
#-------------------------------------------------------------------------------
@app.route('/profile')
def profilePage():
    """ Renders the users profile and is shown immediately after a successful
    user login. It gets the user session object and uses that to link to various
    parts of the internal UI"""
    if session['user']:
        try:
            firstLogin = request.args.get('ref')
        except:
            firstLogin = None;
        GET_IF_FACEBOOK_URL = GET_FACEBOOK_INFO_URL + session['user']['token']
        check_request = requests.get(GET_IF_FACEBOOK_URL)
        check_response = json.loads(check_request.content)
        if str(check_response['Status']['Successful']) == "False":
            facebook_connected = False
        else:
            facebook_connected = True
        return render_template("profile.html", facebook_connected = facebook_connected,
        firstLogin = firstLogin, user = session['user'])
    else:
        return redirect(url_for('loginPage'))
#-------------------------------------------------------------------------------
@app.route('/profile/edit', methods=['GET', 'POST'])
def editProfile():
    """ The edit profile page primarily has four forms. It should be much more
    curt but that's what's required of me. Form 1 information updates the users
    name, username, etc. Form 2 updates both the postal as well as actual users
    address.
    Contact details can be updated using the form 3, and form four simply
    updates the password."""
    from flask import request
    if session['user']:
        user = session['user']
        if request.method == "GET":
            baseUrl = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Customer_Profile&Token='
            getUrl = baseUrl + str(user['token'])
            request = requests.post(getUrl)
            response = json.loads(request.content)
            if response['addresses'][0]['address_type'].lower() == "actual":
                actual_address = response['addresses'][0]
                postal_address = response['addresses'][1]
            else:
                actual_address = response['addresses'][1]
                postal_address = response['addresses'][0]
            if str(response['retmsgs'][0]['eSuccessful']) == "True":
                return render_template("editprofile.html",
                    customer = response['customer'][0],
                    actual_address = actual_address,
                    postal_address = postal_address,
                    user = user)
            else:
                return render_template("errors/500.html")
        elif request.method == "POST":
            form_number = str(request.form['which_form'])
            if form_number == "1":
                POST_URL = GLOBAL_BASE_URL + '/REST-PostReq.awp'
                payload = {}
                headers = {'content-type': 'application/json'}
                headers['token'] = user['token']
                headers['Procedure'] = 'Customer_Profile_Edit'
                payload['customer'] = {'name_first' : request.form['firstname'],
                    'name_last' : request.form['lastname'],
                    'business_name': request.form['business_name'],
                    'timezone': request.form['timezone']}
                r = requests.post(POST_URL, data=json.dumps(payload),
                    headers=headers)
                return redirect(url_for('editProfile',
                    message = "Details Updated Successfully"))
            elif form_number == "2" or form_number == "3":
                POST_URL = GLOBAL_BASE_URL + '/REST-PostReq.awp'
                payload = {}
                headers = {'content-type': 'application/json'}
                headers['token'] = user['token']
                headers['Procedure'] = 'Customer_Profile_Edit'
                payload['addresses'] = [{"address_type":"Actual",
                    "address_line1": request.form['addresslineone'],
                    "address_line2": request.form['addresslinetwo'],
                    "address_city": request.form['city'],
                    "address_region": request.form['state'],
                    "address_postcode": request.form['postal'],
                    "address_country_name": request.form['country']},
                    { "address_type":"Postal",
                    "address_line1": request.form['postal_addresslineone'],
                    "address_line2": request.form['postal_addresslinetwo'],
                    "address_city": request.form['postal_city'],
                    "address_region": request.form['postal_state'],
                    "address_postcode": request.form['postal_postal'],
                    "address_country_name": request.form['postal_country']}]
                r = requests.post(POST_URL, data=json.dumps(payload),
                    headers=headers)
                return redirect(url_for('editProfile',
                    message = "Address Updated Successfully"))
            elif form_number == "4":
                POST_URL = GLOBAL_BASE_URL + '/REST-PostReq.awp'
                payload = {}
                headers = {'content-type': 'application/json'}
                headers['token'] = user['token']
                headers['Procedure'] = 'Customer_Profile_Edit'
                payload['customer'] = {"email": request.form['email_address_c'],
                    "username": request.form['email_address_c'],
                    "mobile_phone_country_cd": request.form['countrycode'],
                    "mobile_phone_number": request.form['mobile_phone_number_c']}
                r = requests.post(POST_URL, data=json.dumps(payload),
                    headers=headers)
                return redirect(url_for('editProfile'))
            elif form_number == "5":
                POST_URL = MODEL_PREFERENCE + user['token']
                payload = {}
                headers = {'content-type': 'application/json'}
                if request.form['password1'] == request.form['password2']:
                    payload = {"model_preference": request.form['password1'],
                        "retired_model": request.form['opmodel']}
                    r = requests.post(POST_URL, data=json.dumps(payload),
                        headers=headers)
                    return redirect(url_for('profilePage'))
                else:
                    return redirect(url_for('editProfile',
                        message = "Passwords Did Not Match"))
            else:
                return render_template("errors/500.html")
    else:
        return redirect(url_for('loginPage'))
#-------------------------------------------------------------------------------
@app.route('/seller/<token>', methods = ['GET', 'POST'])
def sellerListing(token):
    if session['user']:
        user = session['user']
        GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_List&Token=' + token
        request = requests.post(GET_URL)
        print request.content
        products = json.loads(request.content)["products"]
        return render_template("seller.html", products = products,
            token = token, user = user)
    else:
        return redirect(url_for('loginPage'))
#-------------------------------------------------------------------------------
@app.route('/outright/buy/<token>', methods = ['GET', 'POST'])
def buyOutright(token):
    from flask import request
    if request.method == "GET":
        import json
        GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
        request = requests.post(GET_URL)
        product = json.loads(request.content)["product"]
        return render_template("outright/buy.html", product = product[0],
            token = token, guestmode = False)
    elif request.method == "POST":
        session['transaction'] = {'amount': request.form.get('amount'),
            'cost_per_item': request.form.get('cost_per_item'),
            'no_bikes': request.form.get('no_bikes'),
            'part_payment': request.form.get('part_payment'),
            'currency': request.form.get('currency'),
            'name': request.form.get('name'),
            'max_date': request.form.get('max_date')}
        return redirect(url_for('deliveryOutright', token = token))
#-------------------------------------------------------------------------------
@app.route('/outright/delivery/<token>', methods = ['GET', 'POST'])
def deliveryOutright(token):
    if request.method == "GET":
        transaction = session['transaction']
        user = session['user']
        return render_template("outright/delivery.html", transaction = transaction,
            token = token, user = user)
    elif request.method == "POST":
        return "200 OK"
#-------------------------------------------------------------------------------
@app.route('/outright/pay/<token>', methods=['GET', 'POST'])
def payOutright(token):
    if request.method == "GET":
        user = session['user']
        return render_template("outright/pay.html",
            keys = "pk_test_JvYffOKVrAyerfnvecmzjsjr",
            token = user['token'], product_token = token,
            user = user)
    elif request.method == "POST":
        import stripe
        amount = int(request.form['amount_bill']) * 100
        token = request.form['stripeToken']
        stripe.api_key = "sk_test_f5JjDn0WKFAUAtAlolyQyHBs"
        try:
            charge = stripe.Charge.create(
                amount=int(amount),
                currency="AUD",
                description="Skillion Charge",
                source=token,)
            headers = {'content-type': 'application/json'}
            POST_URL = FINAL_PAYMENTS_URL + request.form['orderid']
            payload = {}
            payload["payments"] = {
                "amount_total": int(request.form['amount_bill']),
                "description":"Skillion Charge",
                "payment_method":"Stripe",
                "payment_method_info": str(token), "amount_currency":"AUD"}
            print "\nPayload for Actual Payment: \n"
            print "-----------------"
            print payload
            print "\n-----------------"
            r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
            print "\nWhich returns:"
            print str(json.loads(r.content))
            print "\n\n--------000---------"
            return redirect(url_for('payments', notification="purchased"))
        except Exception as e:
            return redirect(url_for('payments', error=e))
#-------------------------------------------------------------------------------
@app.route('/layby/buy/<token>', methods = ['GET', 'POST'])
def buyLayby(token):
    from flask import request
    if request.method == "GET":
        import json
        GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
        request = requests.post(GET_URL)
        product = json.loads(request.content)["product"]
        return render_template("layby/buy.html", product = product[0],
            token = token, guestmode = False)
    else:
        session['transaction'] = {'amount': request.form.get('amount_pay_now'),
         'amount_total': request.form.get('total_amount'),
         'no_bikes': request.form.get('no_bikes'),
          'part_payment': request.form.get('part_payment'),
          'currency': request.form.get('currency'),
          'name': request.form.get('name'),
           'timeframe': request.form.get('payment_timeframe'),
           'duration': request.form.get('duration'),
           'cost_per_item': request.form.get('cost_per_item'),
            'min_per_txn': request.form.get('min_per_txn'),
            'min_pay': request.form.get('min_pay'),
            'max_date': request.form.get('max_date'),
            'amount_finalpayment': request.form.get('schedule_payment[amount_finalpayment]'),
            'amount_partpayment': request.form.get('schedule_payment[amount_partpayment]'),
            'nbr_of_payments': request.form.get('schedule_payment[nbr_of_payments]'),
            'making_weekly_payment': request.form.get('schedule_payment[making_weekly_payment]')}
        return redirect(url_for('deliveryLayby', token = token))
#-------------------------------------------------------------------------------
@app.route('/layby/delivery/<token>', methods = ['GET', 'POST'])
def deliveryLayby(token):
    if request.method == "GET":
        transaction = session['transaction']
        transaction['contr_per_item'] = int(transaction['amount'])/int(transaction['no_bikes'])
        user = session['user']
        return render_template("layby/delivery.html", transaction = transaction,
            token = token, user = user)
    elif request.method == "POST":
        return "200 OK"
#-------------------------------------------------------------------------------
@app.route('/layby/pay/<token>', methods=['GET', 'POST'])
def payLayby(token):
    product_token = token
    if request.method == "GET":
        user = session['user']
        return render_template("layby/pay.html",
            keys = "pk_test_JvYffOKVrAyerfnvecmzjsjr",
            token = user['token'], product_token = token,
            user = user)
    elif request.method == "POST":
        import stripe
        amount = int(request.form['amount_bill']) * 100
        token = request.form['stripeToken']
        stripe.api_key = "sk_test_f5JjDn0WKFAUAtAlolyQyHBs"
        user = session['user']
        try:
            charge = stripe.Charge.create(
                amount=int(amount),
                currency="AUD",
                description="Skillion Charge",
                source=token,)
            headers = {'content-type': 'application/json'}
            POST_URL = LAYBY_PAYMENTS_URL + user['token']
            payload = json.loads(request.form['ipDump'])
            payload['Payment']['description'] = "Skillion Charge"
            payload['Payment']['payment_ref'] = str(token)

            id_list = json.loads(request.form['idlist'])

            for index, item in enumerate(id_list):
                payload['Line_Items'][index]['id'] = item

            print "\nPayload for Actual Initial Payment: \n"
            print "-----------------"
            print payload
            print POST_URL
            r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
            print "\n-----------------"
            print "\nWhich returns:"
            print str(json.loads(r.content))
            print "\n\n--------000---------"
            if json.loads(r.content)['Status']['Successful'] == True:
                return redirect(url_for('payments', notification="purchased"))
            else:
                return redirect(url_for('payments', error="Something went wrong. Please try again later!"))
        except Exception as e:
            return redirect(url_for('payments', error=e))
#-------------------------------------------------------------------------------
@app.route('/zip/buy/<token>', methods=['GET', 'POST'])
def zipBuy(token):
    from flask import request
    if request.method == "GET":
        st = request.args.get('st', 1)
        import json
        GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
        request = requests.post(GET_URL)
        product = json.loads(request.content)["product"]
        return render_template("zip/buy.html", product = product[0],
            token = token, guestmode = False, st = st)
    else:
        session['transaction'] = {'amount': request.form.get('amount'),
        'cost_per_item': request.form.get('cost_per_item'),
        'no_bikes': request.form.get('no_bikes'),
        'part_payment': request.form.get('part_payment'),
        'currency': request.form.get('currency'),
        'name': request.form.get('name'),
         'max_date': request.form.get('max_date')}
        return redirect(url_for('zipDelivery', token = token))
#-------------------------------------------------------------------------------
@app.route('/zip/delivery/<token>', methods = ['GET', 'POST'])
def zipDelivery(token):
    if request.method == "GET":
        transaction = session['transaction']
        user = session['user']
        return render_template("zip/delivery.html", transaction = transaction,
            token = token, user = user)
    elif request.method == "POST":
        return "200 OK"
#-------------------------------------------------------------------------------
@app.route('/zip/setup', methods=['GET', 'POST'])
def setupZip():
    if request.method == "POST":
        import json
        from flask import jsonify
        data = json.loads(request.form['key'])
        headers = {'content-type': 'application/json'}
        POST_URL = 'https://api.zipmoney.com.au/v1/checkout'
        payload = str(data).replace("'", '"').replace('u"', '"')
        r = requests.post(POST_URL, data=payload, headers=headers)
        return str(json.loads(r.content)['redirect_url'])
    else:
        return "Nothing to see here."
#-------------------------------------------------------------------------------
@app.route('/zipstdby', methods=['GET', 'POST'])
def zipddd():
    return "On Standby"
#-------------------------------------------------------------------------------
@app.route('/zip/pay/<token>', methods=['GET', 'POST'])
def zipPay(token):
    if request.method == "GET":
        user = session['user']
        return render_template("zip/pay.html", token = user['token'],
            product_token = token, user = user)
    if request.method == "POST":
        return redirect(url_for('payments', notification="purchased"))
#-------------------------------------------------------------------------------
@app.route('/zip', methods=['GET', 'POST'])
def preparePayments():
    import json
    from flask import request
    user = session['user']
    payload = {}
    token = request.form['product_token']
    headers = {'content-type': 'application/json'}
    GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
    outbound_R = requests.post(GET_URL)
    seller_id = json.loads(outbound_R.content)["product"][0]["seller_token"]
    payload['order'] = {
        'seller_id': seller_id,
        'customer_token': str(user['token']),
        'amount_total': request.form['amount_total'],
        'amount_paid': request.form['payment_for'],
        'amount_remaining': int(request.form['amount_total']),
        'amount_currency': request.form['currency'],
        'description': request.form['name'],
        'date_due': request.form['due_date'],
        'purchase_qty': request.form['no_bikes'],
        'is_fully_paid': request.form['is_fully_paid']}
    if request.form['is_layby'] == "yes":
        payload['schedule_payment'] = {
             "amount_finalpayment": request.form['amount_finalpayment'],
             "amount_partpayment": request.form['amount_partpayment'],
             "nbr_of_payments": request.form['nbr_of_payments'],
             "making_weekly_payment": request.form['making_weekly_payment']
        }
    else:
        pass
    print "\nPayload for order main: \n"
    print "-----------------"
    print payload
    print "\n-----------------"
    r = requests.post(NEW_ORDER_URL, data=json.dumps(payload), headers=headers)
    print "\nWhich returns:"
    print str(json.loads(r.content))
    print "\n\n--------000---------"
    return str(json.loads(r.content)['order']['id'])
#-------------------------------------------------------------------------------
@app.route('/orderlines', methods=['GET', 'POST'])
def orderlinesThrow():
    if request.method == "POST":
        import json
        jsonified_lines = json.loads(request.form['key']);
        order_id = jsonified_lines['order_id']
        order_lines = jsonified_lines['order_line']
        headers = {'content-type': 'application/json'}
        POST_URL = NEW_ORDERLINE_URL + str(order_id)
        payload = {}
        payload["order_line"] = order_lines
        print "\nPayload for Orderlines: \n"
        print "-----------------"
        print payload
        print "\n-----------------"
        r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
        print "\nWhich returns:"
        print str(json.loads(r.content))
        print "\n\n--------000---------"
        return r.content
    else:
        return "Nothing to see here."
#-------------------------------------------------------------------------------
@app.route('/pay/all/<currency>/<amount>/<id>', methods=['GET', 'POST'])
def payAll(currency, amount, id):
    user = session['user']
    if request.method == "GET":
        return render_template("stripe.html",
            keys = "pk_test_JvYffOKVrAyerfnvecmzjsjr",
            currency = currency, amount = amount, rec = True, id = id,
            user = session['user'])
    if request.method == "POST":
        import stripe
        token = request.form['stripeToken']
        amount = int(request.form['amount']) * 100
        stripe.api_key = "sk_test_f5JjDn0WKFAUAtAlolyQyHBs"
        charge = stripe.Charge.create(
            amount=int(amount),
            currency=str(currency),
            description="Skillion Charge",
            source=token,)
        headers = {'content-type': 'application/json'}
        POST_URL = LAYBY_PAYMENTS_URL + user['token']
        payload = json.loads(request.form['dump'])
        payload['Payment']['payment_ref'] = str(token)
        print "\nPayload for Actual ALL Payment: \n"
        print "-----------------"
        print payload
        r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
        print "\n-----------------"
        print "\nWhich returns:"
        print str(json.loads(r.content))
        print "\n\n--------000---------"
        if json.loads(r.content)['Status']['Successful'] == True:
            return redirect(url_for('payments', notification="purchased"))
        else:
            return redirect(url_for('payments', error="Something went wrong. Please try again later!"))
#-------------------------------------------------------------------------------
@app.route('/pay/recurring/<currency>/<amount>/<id>', methods=['GET', 'POST'])
def payRec(currency, amount, id):
    user = session['user']
    if request.method == "GET":
        return render_template("stripepp.html",
            keys = "pk_test_JvYffOKVrAyerfnvecmzjsjr",
            currency = currency, amount = amount, rec = True, id = id,
            user = session['user'])
    if request.method == "POST":
        import stripe
        token = request.form['stripeToken']
        amount = int(request.form['amount']) * 100
        stripe.api_key = "sk_test_f5JjDn0WKFAUAtAlolyQyHBs"
        charge = stripe.Charge.create(
            amount=int(amount),
            currency=str(currency),
            description="Skillion Charge",
            source=token,)
        headers = {'content-type': 'application/json'}
        POST_URL = LAYBY_PAYMENTS_URL + user['token']
        payload = json.loads(request.form['dump'])
        payload['Payment']['payment_ref'] = str(token)
        print "\nPayload for Actual Part Payment: \n"
        print "-----------------"
        print payload
        r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
        print "\n-----------------"
        print "\nWhich returns:"
        print str(json.loads(r.content))
        print "\n\n--------000---------"
        if json.loads(r.content)['Status']['Successful'] == True:
            return redirect(url_for('payments', notification="purchased"))
        else:
            return redirect(url_for('payments', error="Something went wrong. Please try again later!"))
#-------------------------------------------------------------------------------
@app.route('/payments')
def payments():
    from flask import request
    if request.method == "GET":
        if session['user']:
            try:
                error = request.args.get('error')
            except:
                error = None
            try:
                success = request.args.get('notification')
            except:
                success = None
            user = session['user']
            GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Customer_PaymentList&Token=' + user['token']
            request = requests.post(GET_URL)
            response = json.loads(request.content)
            if str(response['Status']['Successful']) == "True":
                return render_template("payments.html", payments = response['payment'],
                success = success, error = error, user = user)
            else:
                return render_template('errors/nopayments.html')
        else:
            return redirect(url_for('loginPage'))
    else:
        return render_template('errors/500.html')
#-------------------------------------------------------------------------------
@app.route('/purchases')
def purchases():
    if session['user']:
        user = session['user']
        GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Customer_PurchasesList&Token=' + user['token']
        request = requests.post(GET_URL)
        response = json.loads(request.content)
        print response['purchase'][0]
        if str(response['Status']['Successful']) == "True":
            return render_template("purchases.html", purchases = response['purchase'],
                scheduled_payments = response['purchase'][0]['schedule_payment'],
                user = user)
        else:
            return render_template("errors/nopurchase.html")
    else:
        return redirect(url_for('loginPage'))
#-------------------------------------------------------------------------------
@app.route('/guest/<a_token>/<nextmode>', methods = ['GET', 'POST'])
def guestMode(a_token, nextmode):
    import json
    token = a_token.upper()
    from flask import request
    if request.method == "GET":
        if nextmode == "outright":
            GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
            request = requests.post(GET_URL)
            product = json.loads(request.content)["product"]
            print product
            return render_template("outright/buy.html", product = product[0],
                token = token, guestmode = True)
        elif nextmode == "layby":
            GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
            request = requests.post(GET_URL)
            product = json.loads(request.content)["product"]
            #return redirect(url_for('loginPage'))
            return render_template("layby/buy.html", product = product[0],
                token = token, guestmode = True)
        elif nextmode == "zip":
            GET_URL = GLOBAL_BASE_URL + '/REST-Customer.awp?Procedure=Product_Details&Token=' + token
            pr_req = requests.post(GET_URL)
            product = json.loads(pr_req.content)["product"]
            return render_template("zip/buy.html", product = product[0],
                token = token, guestmode = True)
        else:
            return render_template('errors/404.html')
    else:
        return render_template('error/500.html')
#-------------------------------------------------------------------------------
@app.route('/guest/signup', methods = ['GET', 'POST'])
def guestSignUp():
    if request.method == "GET":
        return render_template("guest/signup.html")
    elif request.method == "POST":
        first = request.form['firstname']
        last = request.form['lastname']
        email = request.form['email']
        timezone = request.form['timezone']
        countrycode = request.form['countrycode']
        number = request.form['number']
        paymentType = request.form['paymentType']
        paymentToken = request.form['paymentToken']
        dob = request.form['b_date'] + "-" + request.form['b_month'][:3] + "-" + request.form['b_year']
        headers = {'content-type': 'application/json'}
        payload = {}
        payload["customer"] = {"name_first": first, "name_last": last,
           "username": email, "email": email,
            "mobile_phone_country_cd": countrycode, "timezone": timezone,
            "mobile_phone_number": number, "dob": dob}
        r = requests.post(NEW_CUSTOMER_URL, data=json.dumps(payload), headers=headers)
        print str(r.content)
        if str(json.loads(r.content)["Status"]["Successful"]) == "True":
            response_W = json.loads(r.content)
            session['user'] = response_W['Customer']
            session['user']['dob_zipmoney'] = response_W['dob_zipmoney']
            if paymentType == "outright":
                return redirect(url_for('deliveryOutright', token = paymentToken))
            elif paymentType == "layby":
                return redirect(url_for('deliveryLayby', token = paymentToken))
            elif paymentType == "zip":
                return redirect(url_for('zipDelivery', token = paymentToken))
            else:
                return render_template("error/404.html")
        else:
            return redirect(url_for('loginPage', error = "You already have an account. Log in instead."))

#-------------------------------------------------------------------------------
@app.errorhandler(404)
def pageNotFound(e):
    return render_template('errors/404.html'), 404
#-------------------------------------------------------------------------------
@app.errorhandler(500)
def internalError(e):
    return render_template('errors/500.html'), 500
#-------------------------------------------------------------------------------
@app.route('/callback/zip/primary', methods=['GET', 'POST'])
def primaryZipCallback():
    if request.method == "POST":
        import json
        req_dump = json.loads(request.data)
        print req_dump
        innerReq = json.loads(req_dump["Message"])
        if req_dump["Subject"] == "charge_succeeded":
            orderid = innerReq['response']['order_id']
            POST_URL = FINAL_PAYMENTS_URL + orderid
            payload = {}
            headers = {'content-type': 'application/json'}
            payload["payments"] = {
                "amount_total": 4950,
                "description":"Skillion Charge",
                "payment_method":"ZipMoney",
                "payment_method_info": innerReq['response']['txn_id'], "amount_currency":"AUD"}
            r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
            return "200 OK"
        elif req_dump["Subject"] == "authorise_under_review":
            return "200 OK"
        elif req_dump["Subject"] == "authorise_approved":
            orderid = innerReq['response']['order_id']
            POST_URL = FINAL_PAYMENTS_URL + orderid
            payload = {}
            headers = {'content-type': 'application/json'}
            payload["payments"] = {
                "amount_total": 4950,
                "description":"Skillion Charge",
                "payment_method":"ZipMoney",
                "payment_method_info": innerReq['response']['txn_id'], "amount_currency":"AUD"}
            r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
            return "200 OK"
        elif req_dump["Subject"] == "authorise_declined":
            orderid = innerReq['response']['order_id']
            POST_URL = ZIP_DECLINE_URL + orderid
            payload = {}
            headers = {'content-type': 'application/json'}
            payload["aint_no_sunshine"] = "when sheeeeeez gooooone"
            r = requests.post(POST_URL, data=json.dumps(payload), headers=headers)
            return "200 OK"
    else:
        return render_template('errors/success.html')
#-------------------------------------------------------------------------------
@app.route('/api/v1/schedule', methods = ['GET', 'POST'])
def getSchedule():
    if request.method == "POST":
        headers = {'content-type': 'application/json'}
        payload = {
            "amount_total": int(request.form['amount_total']),
            "amount_deposit": int(request.form['amount_deposit']),
            "nbr_of_payments": int(request.form['nbr_of_payments'])
        }
        r = requests.post(SCHEDULE_URL, data=json.dumps(payload), headers=headers)
        return r.content
    else:
        return "500"
#-------------------------------------------------------------------------------
@app.route('/api/v1/status')
def isLogged():
    if len(session) == 0:
        return jsonify(logged = False)
    else:
        if session['user']:
            if session['user'] != "":
                return jsonify(logged = True)
            else:
                return jsonify(logged = False)
        else:
            return jsonify(logged = False)
#-------------------------------------------------------------------------------
@app.route('/callback/zip/cancel')
def callbackZipCancel():
    return render_template('errors/cancel.html')
#-------------------------------------------------------------------------------
@app.route('/callback/zip/success')
def callbackZipSuccess():
    return render_template('errors/success.html')
#-------------------------------------------------------------------------------
@app.route('/zip/information')
def information():
    return render_template('information.html')
#-------------------------------------------------------------------------------
@app.route('/callback/zip/decline')
def callbackZipDecline():
    return render_template('errors/decline.html')
#-------------------------------------------------------------------------------
@app.route('/privacy')
def privacyPolicy():
    return render_template('errors/privacy.html')
#-------------------------------------------------------------------------------
@app.route('/api/v1/bomb')
def sendBB():
    vid_id = request.args.get('email_id', 0)
    email = request.args.get('email', 0)
    if vid_id != 0 and email != 0:
        try:
            URL = "https://app.bombbomb.com/app/api/api.php?method=SendEmailToEmailAddress&email=nate@skillionbikes.com&pw=Skillion102&email_id=%s&email_address=%s" % ( vid_id, email )
            r = requests.get(URL)
            return r.content
        except Exception as e:
            return e
    else:
        return jsonify(message = "Incorrectly formatted input")
#-------------------------------------------------------------------------------
@app.route('/tos')
def tos():
    return render_template('errors/tos.html')

def sendBombbomb(email, videoId):
    try:
        URL = "https://app.bombbomb.com/app/api/api.php?method=SendEmailToEmailAddress&email=nate@skillionbikes.com&pw=Skillion102&email_id=%s&email_address=%s" % ( vid_id, email )
        r = requests.get(URL)
        return r.content
    except Exception as e:
        return e


if __name__ == "__main__":
    app.run(debug=True)
