from django.shortcuts import render
from .models import *
import json, binascii,os
from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from random import choice
from manager.activity import *
from services.models import *

# Create your views here.

def send_fcm_notification(token,payload,app):
    path_to_fcm = "https://fcm.googleapis.com"
    server_key = "AAAAVNuyMRs:APA91bGlSX3wcrVGhRl2V1XV1mRgN2_3iM0bkp-xhOda65LKARyEZZQzzmH-TRHqAyraxeNCIFU24K0gPUxMa-xIZR7oI7KTAe51vdn_NTlqvNxNFDAWEjgEQdqc6mH1-oZ8w5JbyU-C"
    reg_id = token
    message_title = payload['title']
    message_body = payload['body']
    raw = FCMNotification(api_key=server_key).notify_single_device(registration_id=reg_id, message_title=message_title, message_body=message_body)
    try:
        data = raw.json()
    except:
        data = raw
    return data


home_link = "https://jidi.pywe.org"

def gen_order_no(number):
    if number > 0:
        no = str(number+10000)
    else:
        no = str(10000)
    return no.rjust(12, '0')



def make_payment(request,email):
    user = CustomUser.objects.get(username=email)
    args = {}
    template = "make-payment.html"
    args['zanzama'] = "ZTQwZTUxZjEwMTE2ZTQ1YmJmZjk5ZjY1NDUxOWEzMTY="
    args['user']=user
    number = len(Transaction.objects.all())
    tid = gen_order_no(number)
    args['transaction_id']=tid
    t = Transaction()
    t.transaction_id = tid
    t.save()
    return render(request,template,args)


import requests as r

@csrf_exempt
def verifyTopup(request):
    data = {}
    json_data = json.loads(str(request.body, encoding='utf-8'))
    objects = {}
    for key,val in json_data.items():
        objects[key]=val
    # who is making the request
    try:
        user = CustomUser.objects.get(username=objects['username'])
    except Exception as e:
        data['success']=False
        data['message']="Please login"
        dump = json.dumps(data,cls=ExtendedEncoder)
        return HttpResponse(dump, content_type='application/json')
    transid = objects['transaction_id']
    # make payswitch request
    url = "https://prod.theteller.net/v1.1/users/transactions/{}/status/".format(transid)
    header = {'Merchant-Id':"TTM-00000278"}
    response = r.get(url,headers=header)
    json_data = json.loads(response.text)
    # we got a response, let's go
    """Check if transaction was succesful first"""
    amount = json_data['amount']
    source = json_data['subscriber_number']
    # network = json_data['r_switch']
    status = json_data['status']
    reason = json_data['reason']
    # code = json_data['code']
    # code=100&status=Declined&transaction_id=100000062142 (when it is declined)
    try:
        transaction = Transaction.objects.get(transaction_id=transid)
    except:
        data['success']=False
        data['message']="Transaction ID is not recognized"
        dump = json.dumps(data,cls=ExtendedEncoder)
        return HttpResponse(dump, content_type='application/json')
    transaction.amount = float(amount)
    # transaction.source = source
    # transaction.network = network
    # Let's get the user afresh using the phone
    transaction.user = user
    transaction.status = status
    transaction.account = source
    transaction.transaction_type = "topup"
    user_credit = Wallet.objects.get(user=user)
    tax = 0.0
    total = transaction.amount + tax
    if status == "approved" and user_credit.last_transid != transid:
    # if True:
        transaction.completed = True
        user_credit.last_transid = transid
        user_credit.service_account += float(amount)
        user_credit.save()
        transaction.save()
        # Getting receipt Email and writing it to a file
        # noti = Notify()
        # to user
        # emails = [user.email]
        # email_subject = "Receipt"
        # extra_args = {'user':user,'website_address':"https://www.pywe.org","transaction":transaction,"total":total,"tax":tax,'time':datetime.now()}
        # try:
        #     noti.email_users_only_emails(emails,email_subject,extra_args)
        # except:
        #     pass
        data['success']=True
        data['message']="Successfully topped up"
    else:
        if user_credit.last_transid == transid:
            data['success']=False
            data['message']="Transaction ID has been used"
            dump = json.dumps(data,cls=ExtendedEncoder)
            return HttpResponse(dump, content_type='application/json')
        user_credit.last_transid = transid
        data['success']=False
        data['message']="Transaction was not successfully"
        # transaction.status = False
    dump = json.dumps(data,cls=ExtendedEncoder)
    return HttpResponse(dump, content_type='application/json')

def gen_otp(length):
    token = ''.join([choice('0123456789') for i in range(length)])
    return token

def makeGhanaPhone(inp):
        ph = inp.strip()
        phone = ph.replace(" ","")
        if phone.startswith("+") and len(phone) == 13:
            newphone = phone.replace("+","",1)
        elif phone.startswith("0") and len(phone) == 10:
            # TODO: Remember to handle more countries here, let caller pass the country name in payload
            newphone = phone.replace("0","233",1)
        elif phone.startswith("O") and len(phone) == 10:
            # TODO: Remember to handle more countries here, let caller pass the country name in payload
            newphone = phone.replace("O","233",1)
        elif phone.startswith("233") and len(phone) == 12:
            newphone = phone
        elif phone == "None":
            newphone = ""
        elif len(phone) == 9:
            newphone = "233"+phone
        else:
             newphone = phone
        return newphone



# Create your views here.
@csrf_exempt
def registerUser(request):
    # Getting data posted by user
    json_data = json.loads(str(request.body, encoding='utf-8'))
    data = {}
    response = {}
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        data[key]=val
    # let's try the phone
    try:
        CustomUser.objects.get(username=data['email'])
    except:
        # all clear, lets create a new user
        try:
            user = CustomUser()
            # user.phone = makeGhanaPhone(data['phone'])
            # username = objects['username']
            user.username = data['email'].split("@")[0]
            # user.full_name = data['full_name']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.notification_token = data['notification_token']
            # user.otp = gen_otp(4)
            user.save()
            user.set_password(data['password'])
            user.save()
            # create credit
            wallet = Wallet()
            wallet.user = user
            wallet.save()
        except Exception as e:
            response['success']=False
            if "Duplicate entry" in str(e):
                response['message']="Sorry, account name or phone is already taken"
            else:
                response['message']=str(e)
        else:
            # TODO: send both email and sms here
            # response['success']=True
            # response['message']="Successfully registered."
            # response['user']=user
            u = authenticate(request,username=data['email'],password=data['password'])
            login(request,u)
            myuser = {}
            userData = {}
            userData['username']=user.username
            userData['id']=user.id
            userData['full_name']=user.first_name + " " + user.last_name
            userData['first_name']=user.first_name
            userData['last_name']=user.last_name
            userData['email']=user.email
            userData['is_professional']=user.is_professional
            # userData['verified']=user.verified
            userData['active']=user.is_active
            # userData['is_staff']=user.is_staff
            # userData['is_superuser']=user.is_superuser
            myuser['user']=userData
            wall = {}
            wall['topup_account']=wallet.topup_account
            wall['service_account']=wallet.service_account
            myuser['wallet']=wall
            response['success']=True
            response['message']="Login successful"
            response['user']=myuser
            # msg = "Welcome to Jidi, this is your one time password(OTP) {}".format(user.otp)
            # phones = [user.phone]
            # payload = {'body':msg,'phone':phones}
            # try:
            #     noti.send_sms(payload)
            # except:
            #     pass
            # token = user.notification_token
            # msg = "You are welcome to Jidi Food Delivery. Your OTP is {}".format(user.otp)
            # app = "Jidi"
            # fcm_payload = {'title':'Succesfully Registered','body':msg}
            # try:
            #     send_fcm_notification(token,fcm_payload,app)
            # except:
            #     pass
    else:
        # we got a user with the same phone number
        response['success']=False
        response['message']="A user with same phone number exists"
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def registerProfessional(request):
    # Getting data posted by user
    json_data = json.loads(str(request.body, encoding='utf-8'))
    data = {}
    response = {}
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        data[key]=val
    # let's try the phone
    try:
        CustomUser.objects.get(username=data['email'])
    except:
        # all clear, lets create a new user
        try:
            user = Practitioner()
            # user.phone = makeGhanaPhone(data['phone'])
            user.username = data['email'].split("@")[0]
            # user.full_name = data['full_name']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.is_professional = True
            user.notification_token = data['notification_token']
            user.practice = Practice.objects.first()
            # user.otp = gen_otp(4)
            user.save()
            user.set_password(data['password'])
            user.save()
            # create credit
            wallet = Wallet()
            wallet.user = user
            wallet.save()
        except Exception as e:
            response['success']=False
            if "Duplicate entry" in str(e):
                response['message']="Sorry, account name or phone is already taken"
            else:
                response['message']=str(e)
        else:
            # TODO: send both email and sms here
            # response['success']=True
            # response['message']="Successfully registered."
            # response['user']=user
            u = authenticate(request,username=data['email'],password=data['password'])
            login(request,u)
            myuser = {}
            userData = {}
            userData['username']=user.username
            userData['id']=user.id
            userData['full_name']=user.first_name + " " + user.last_name
            userData['first_name']=user.first_name
            userData['last_name']=user.last_name
            userData['email']=user.email
            # userData['verified']=user.verified
            userData['active']=user.is_active
            userData['is_professional']=user.is_professional
            # userData['is_staff']=user.is_staff
            # userData['is_superuser']=user.is_superuser
            myuser['user']=userData
            wall = {}
            wall['topup_account']=wallet.topup_account
            wall['service_account']=wallet.service_account
            myuser['wallet']=wall
            response['success']=True
            response['message']="Login successful"
            response['user']=myuser
            # msg = "Welcome to Jidi, this is your one time password(OTP) {}".format(user.otp)
            # phones = [user.phone]
            # payload = {'body':msg,'phone':phones}
            # try:
            #     noti.send_sms(payload)
            # except:
            #     pass
            # token = user.notification_token
            # msg = "You are welcome to Jidi Food Delivery. Your OTP is {}".format(user.otp)
            # app = "Jidi"
            # fcm_payload = {'title':'Succesfully Registered','body':msg}
            # try:
            #     send_fcm_notification(token,fcm_payload,app)
            # except:
            #     pass
    else:
        # we got a user with the same phone number
        response['success']=False
        response['message']="A user with same phone number exists"
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def loginUser(request):
    # Getting data posted by user
    json_data = json.loads(str(request.body, encoding='utf-8'))
    objects = {}
    response = {}
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        objects[key]=val
    username = objects['email'].split("@")[0]
    user = authenticate(request,username=username,password=objects['password'])
    if user is not None:
        login(request,user)
        myuser = {}
        userData = {}
        userData['username']=user.username
        userData['id']=user.id
        userData['full_name']=user.first_name + " " + user.last_name
        userData['first_name']=user.first_name
        userData['last_name']=user.last_name
        userData['email']=user.email
        userData['is_professional']=user.is_professional
        # userData['verified']=user.verified
        userData['active']=user.is_active
        # userData['is_staff']=user.is_staff
        # userData['is_superuser']=user.is_superuser
        myuser['user']=userData
        wallet = Wallet.objects.get(user=user)
        wall = {}
        wall['topup_account']=wallet.topup_account
        wall['service_account']=wallet.service_account
        myuser['wallet']=wall
        response['success']=True
        response['message']="Login successful"
        response['user']=myuser
    else:
        response['success']=False
        response['message']="Login failed. Please check your credentials."
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def getUser(request):
    json_data = json.loads(str(request.body, encoding='utf-8'))
    objects = {}
    response = {}
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        objects[key]=val
    username = objects['username'].split("@")[0]
    try:
        user = CustomUser.objects.get(username=username)
    except:
        response['success']=False
        response['message']="Could not find user"
    else:
        myuser = {}
        userData = {}
        userData['username']=user.username
        # userData['phone']=user.phone
        userData['full_name']=user.first_name + " " + user.last_name
        # userData['verified']=user.verified
        userData['active']=user.is_active
        userData['is_professional']=user.is_professional
        # userData['is_staff']=user.is_staff
        # userData['is_superuser']=user.is_superuser
        myuser['user']=userData
        try:
            wallet = Wallet.objects.get(user=user)
        except:
            wallet = Wallet()
            wallet.username = user.username
            wallet.save()
        wall = {}
        wall['topup_account']=wallet.topup_account
        wall['service_account']=wallet.service_account
        myuser['wallet']=wall
        response['success']=True
        response['message']="Login successful"
        response['user']=myuser
        # noti = Notify()
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def chargeUser(request):
    json_data = json.loads(str(request.body, encoding='utf-8'))
    objects = {}
    response = {}
    wall = {}
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        objects[key]=val
    username = objects['username'].split("@")[0]
    try:
        user = CustomUser.objects.get(username=username)
    except:
        response['success']=False
        response['message']="Could not find user"
    else:
        try:
            wallet = Wallet.objects.get(user=user)
        except:
            wallet = Wallet()
            wallet.username = user.username
            wallet.save()
        # let's get the order they are paying for
        try:
            order = Request.objects.get(id=int(objects['order_number']))
        except Exception as e:
            response['success']=False
            response['message']=str(e)
            dump = json.dumps(response,cls=ExtendedEncoderAllFields)
            return HttpResponse(dump, content_type='application/json')

        # check if we can charge the account
        if not order.paid:
            if wallet.service_account >= float(objects['total_charge']):

                wall['previous_service_account']=wallet.service_account
                wall['previous_topup_account']=wallet.topup_account
                wallet.service_account -= float(objects['total_charge'])
                wallet.save()
                order.paid = True
                order.status = "Paid"
                order.save()

                response['success']=True
                response['message']="Account charged successfully!"
                # noti = Notify()
                # token = user.notification_token
                # msg = "GHC {} has been charged from your Jidi Food Wallet. Thank you!".format(objects['total_charge'])
                # app = "Jidi"
                # fcm_payload = {'title':'Wallet Charged','body':msg}
                # try:
                #     send_fcm_notification(token,fcm_payload,app)
                # except:
                #     pass
            else:
                response['success']=False
                response['message']="Not enough balance"
                dump = json.dumps(response,cls=ExtendedEncoderAllFields)
                return HttpResponse(dump, content_type='application/json')
        else:
            response['success']=False
            response['message']="Order already paid for"
        wall['topup_account']=wallet.topup_account
        wall['service_account']=wallet.service_account
        response['wallet']=wall
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def getTransactions(request):
    objects = {}
    response = {}
    try:
        json_data = json.loads(str(request.body, encoding='utf-8'))
    except:
        response['success']=False
        response['message']="Expected some payload/request body, but did not get any from you"
        response['code']=403
        dump = json.dumps(response,cls=ExtendedEncoderAllFields)
        return HttpResponse(dump, content_type='application/json')
    # putting data posted by user into our own dictionary
    for key,val in json_data.items():
        objects[key]=val
    phone = json_data['phone']
    try:
        user = CustomUser.objects.get(phone=phone)
    except:
        response['success']=False
        response['message']="Could not get user"
        dump = json.dumps(response,cls=ExtendedEncoderAllFields)
        return HttpResponse(dump, content_type='application/json')
    # get orders
    response['objects']=[{'transaction':i,'date':i.date_created.date().strftime('%b %d, %Y'),'time':i.date_created.time().strftime('%I:%M %p')} for i in Transaction.objects.filter(user=user)][::-1]
    response['success']=True
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')