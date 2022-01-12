from django.shortcuts import render,HttpResponse
import re
from difflib import SequenceMatcher as sm
from manager.activity import *
from .models import *
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
import requests as r
from django.contrib import messages
# from accounts.models import Transaction
from random import sample
from math import cos, asin, sqrt
from accounts.models import CustomUser, Practice, Practitioner
# from .fcm import FCMNotification



# def send_fcm_notification(token,payload,app):
#     path_to_fcm = "https://fcm.googleapis.com"
#     server_key = "AAAAVNuyMRs:APA91bGlSX3wcrVGhRl2V1XV1mRgN2_3iM0bkp-xhOda65LKARyEZZQzzmH-TRHqAyraxeNCIFU24K0gPUxMa-xIZR7oI7KTAe51vdn_NTlqvNxNFDAWEjgEQdqc6mH1-oZ8w5JbyU-C"
#     reg_id = token
#     message_title = payload['title']
#     message_body = payload['body']
#     raw = FCMNotification(api_key=server_key).notify_single_device(registration_id=reg_id, message_title=message_title, message_body=message_body)
#     try:
#         data = raw.json()
#     except:
#         data = raw
#     return data

# Create your views here.

decided_c = 5

def distance(lat1, lon1, lat2, lon2):
    # exceptions = ["Pharst Care Ghana"]
    # if pharm_name in exceptions:
    #     return 0
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a)) #2*R*asin...

def ratio_match(user,existing):
    return sm(None,user,existing).ratio()


class Searcher:
    def __init__(self):
        pass

    def my_searcher(self,all_from_db,user_prov):
        my_dict = {}
        for index,each in enumerate(all_from_db):
            ratio = self.ratio_match(user_prov,each)
            if ratio >= .6:
                #my_dict.clear()
                my_dict[each]=ratio
        return my_dict


    def ratio_match(self,user,existing):
        from difflib import SequenceMatcher as sm
        return sm(None,user,existing).ratio()

    def my_matcher(self, all_msgs,new_msg,bot_ratio=0.5):
        my_dict = {'0':0}
        for index,each_msg in enumerate(all_msgs):
            ratio = self.ratio_match(new_msg,each_msg)
            if ratio > bot_ratio and ratio > list(my_dict.values())[0]:
                my_dict.clear()
                my_dict[each_msg]=ratio
        return my_dict



def pat_search(user,my_list):
    words = []
    my = re.compile(r'{}'.format(user),re.IGNORECASE)
    for i in my_list:
        a = my.search(i)
        if a:
            words.append(i)
            # print(a.group())
    words.sort()
    return words



def getItemsbyTitle(name,array):
    return array.filter(title=name)


def sort_by_promotion(item):
    return item['promoted']

def sort_by_rating(item):
    return item['rating']

def sort_by_charge(item):
    return item['charge']


def sort_by_distance(item):
    return item['distance']



@csrf_exempt
def fetchbyCategory(request):
    data = {}
    json_data = json.loads(str(request.body, encoding='utf-8'))
    try:
        q = json_data['q']
    except:
        data['success']=False
        data['message']= "No search word provided"
        data['code']= 403
        dump = json.dumps(data,cls=ExtendedEncoderAllFields)
    try:
        area =Practice.objects.get(id=int(q))
    except:
        objs = []
    else:
        objs = [model_to_dict(i) for i in area.professionals.all()]
        for i in objs:
            # if i.date_and_time:
            #     i['month'] = i.date_and_time.strftime("%b")
            i['category']=area
            del i['user_permissions']
            del i['groups']
            del i["password"]
            del i["last_login"]
            del i["is_superuser"]
            del i["is_staff"]
            del i["is_active"]
            del i["phone"]
            del i["otp"]
            del i["email"]
            del i["date_joined"]
            del i["notification_token"]
            del i["customuser_ptr"]
            del i["practice"]
            # i['gallery'] = [model_to_dict(e) for e in Fixer.objects.get(id=int(i['id'])).gallery.all()]
            # i['ratings'] = [model_to_dict(e) for e in Practitioner.objects.get(id=int(i['id'])).ratings.all()]
            # i['services'] = [model_to_dict(e) for e in Fixer.objects.get(id=int(i['id'])).services.all()]
            # if i['location_type'] == "physical":
            #     lat = json_data['latitude']
            #     lon = json_data['longitude']
            #     fixer_lat = i['latitude']
            #     fixer_lon = i['longitude']
            #     i['distance']=round(distance(lat,lon,fixer_lat,fixer_lon),2)
            # else:
            #     i['distance']=0
            # for e in i['ratings']:
            #     e['rated_by'] = model_to_dict(CustomUser.objects.get(id=int(e['rated_by'])))
    objs.sort(key=sort_by_rating)
    # objs.sort(key=sort_by_charge,reverse=True)
    # objs.sort(key=sort_by_promotion,reverse=True)
    # page = int(json_data['page'])
    # start = (decided_c*page)-decided_c
    # end = decided_c*page
    # objs = objs[start:end]
    # data = {}
    # if len(objs) < decided_c:
    #     data['end'] = True
    # else:
    #     data['end']=False
    data['success']=True
    data['message']=str(len(objs))+" results retrieved"
    data['code']=201
    data['objects'] = objs
    dump = json.dumps(data,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def fetchAllCategories(request):
    data = {}
    areas = [i for i in Practice.objects.all()]
    data['success']=True
    data['message']=str(len(areas))+" results retrieved"
    data['code']=201
    data['objects'] = areas
    dump = json.dumps(data,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


# @csrf_exempt
# def fetchPromoted(request):
#     data = {}
#     promoted = [model_to_dict(i) for i in Fixer.objects.filter(promoted=True)]
#     for i in promoted:
#         i['category']=Category.objects.get(id=int(i['category']))
#         i['gallery'] = [model_to_dict(e) for e in Fixer.objects.get(id=int(i['id'])).gallery.all()]
#         i['ratings'] = [model_to_dict(e) for e in Fixer.objects.get(id=int(i['id'])).ratings.all()]
#         i['services'] = [model_to_dict(e) for e in Fixer.objects.get(id=int(i['id'])).services.all()]
#         for e in i['ratings']:
#             e['rated_by'] = model_to_dict(CustomUser.objects.get(id=int(e['rated_by'])))
#     data['success']=True
#     data['message']=str(len(promoted))+" results retrieved"
#     data['code']=201
#     data['objects'] = promoted
#     dump = json.dumps(data,cls=ExtendedEncoderAllFields)
#     return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def createRequest(request):
    data = {}
    json_data = json.loads(str(request.body, encoding='utf-8'))
    # create a new request
    req = Request()
    req.message = json_data['problem']
    req.consultation_fee = float(json_data['fee'])
    req.save()
    # get the patient
    patient = CustomUser.objects.get(username=json_data['patient'])
    pro = CustomUser.objects.get(id=int(json_data['professional']))
    req.patient = patient
    req.professional = pro
    req.save()
    # now we alert the professional
    # token = pro.notification_token
    # msg = "Hello there, you have a new request."
    # app = "HealthNow"
    # fcm_payload = {'title':'New Request','body':msg}
    # try:
    #     send_fcm_notification(token,fcm_payload,app)
    # except:
    #     pass
    data['success']=True
    data['message']="Request has been created, wait for professional's response please."
    dump = json.dumps(data,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


@csrf_exempt
def updateRequest(request):
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
    # get the signature
    reply = objects['accepted']
    id = objects['id']
    order = Request.objects.get(id=int(id))
    if reply:
        order.accepted = True
        # is there a google meeting link?
        try:
            meet = objects['meeting_link']
        except:
            pass
        else:
            order.meeting_link = meet
            order.save()
        pro = Practitioner.objects.get(username=order.professional.username)
        pro.appointments += 1
        pro.save()
        order.status = "accepted"
    else:
        order.status = "declined"
        order.declined = True
    order.save()
    # let's inform the user about what happened to their request
    response['success']=True
    response['message']="Request updated"
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def rateProfessional(request):
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
    # get the signature
    no = objects['id']
    rating = objects['rating']
    order = Request.objects.get(id=int(no))
    order.attended_to = True
    order.rating = int(rating)
    order.save()
    try:
        feedback = objects['feedback']
    except:
        pass
    else:
        order.feedback = feedback
        order.save()
    response['success']=True
    response['message']="Request rated"
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def getRequests(request):
    users = CustomUser.objects.all()
    # for i in users:
    #     try:
    #         i.username = i.username.split("@")[0]
    #         i.save()
    #     except:
    #         i.username = i.username.split("@")[0]+"1"
    #         i.save()
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
    username = objects['username'].split("@")[0]
    user = CustomUser.objects.get(username=username)
    reqs = user.requests.all()
    reqss = []
    if len(reqs) < 1:
        reqss = [model_to_dict(i) for i in user.my_requests.all()]
    else:
        reqss = [model_to_dict(i) for i in user.requests.all()]
    response['success']=True
    objs = []
    for i in reqss:
        i['patient_username']=CustomUser.objects.get(id=int(i['patient'])).username
        i['professional_username']=CustomUser.objects.get(id=int(i['professional'])).username
        objs.append(i)
    response['objects']=objs
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')



@csrf_exempt
def createMessage(request):
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
    msg = Message()
    r_username = json_data['recipient_id'].split("@")[0]
    s_username = json_data['sender_id'].split("@")[0]
    recipient = CustomUser.objects.get(username=r_username)
    sender = CustomUser.objects.get(username=s_username)
    msg.sender = sender
    msg.recipient = recipient
    msg.message = json_data['message']
    msg.sent = True
    msg.save()
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')


def sort_by_id(item):
    return item['id']


@csrf_exempt
def readMessage(request):
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
    r_username = json_data['receiver'].split("@")[0]
    s_username = json_data['sender'].split("@")[0]
    user = CustomUser.objects.get(username=r_username)
    sender = CustomUser.objects.get(username=s_username)
    msgs = Message.objects.filter(recipient=user,sender=sender,received=False)
    objs = []
    a = [model_to_dict(i) for i in msgs]
    # ab_msgs = Message.objects.filter(sender=user,recipient=sender)
    # ab =  [model_to_dict(i) for i in ab_msgs]
    # a.extend(ab)
    for e in msgs:
        e.received = True
        e.sent = True
        e.save()
    # for e in ab_msgs:
    #     e.received = True
    #     e.sent = True
    #     e.save()

    for msg in a:
        msg['sender'] = CustomUser.objects.get(id=int(msg['sender'])).username
        msg['recipient'] = CustomUser.objects.get(id=int(msg['recipient'])).username
        objs.append(msg)
    objs.sort(key=sort_by_id)
    response['objects'] = objs
    dump = json.dumps(response,cls=ExtendedEncoderAllFields)
    return HttpResponse(dump, content_type='application/json')






