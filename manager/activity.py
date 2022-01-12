from django.shortcuts import render,redirect,HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import ImageFieldFile,FieldFile
from django.forms import model_to_dict
from django.apps import apps
from django.template.loader import render_to_string
from accounts.models import Email
from webpush import send_user_notification
from django.core.mail import send_mail
from random import choice
from fcm_django.models import FCMDevice
import requests as r

def concat(a, b):
    yield from a
    yield from b


my_apps = ['accounts','manager','services']

every_app = []
for each in my_apps:
    every_app.extend(apps.get_app_config(each).get_models())
objects = {}
for model in every_app:
    objects[model.__name__]=model


class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ImageFieldFile):
            try:
                mypath = o.path
            except:
                return ''
            else:
                return mypath
        # this will either recusively return all atrributes of the object or return just the id
        elif isinstance(o, Model):
            # return model_to_dict(o)
            return o.id

        return super().default(o)

class ExtendedEncoderAllFields(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, ImageFieldFile):
            try:
                mypath = o.url
            except:
                return ''
            else:
                return mypath
        if isinstance(o, FieldFile):
            try:
                mypath = o.url
            except:
                return ''
            else:
                return mypath
        # this will either recusively return all atrributes of the object or return just the id
        elif isinstance(o, Model):
            return model_to_dict(o)
            # return o.id
        return super().default(o)


        return super().default(o)


def getRelatedName(model,field):
    "Get the model to which a field is related"
    return model._meta.get_field(field).related_model.__name__


def raltionship(model,field):
    "What relationship does this field hold"
    if model._meta.get_field(field).many_to_one:
        return "many_to_one"
    elif model._meta.get_field(field).many_to_many:
        return "many_to_many"
    elif model._meta.get_field(field).one_to_one:
        return "one_to_one"
    elif model._meta.get_field(field).one_to_many:
        return "one_to_many"
    else:
        return "no_relation"




class Activity:
    # class constructor, initializer
    def __init__(self,modelName):
        self.modelName = modelName
        self.objects = objects

    # class method
    def create(self,**kwargs):
        # model = apps.get_model('Accounts', self.modelName)
        try:
            # creating instance as django model object based on passed modelName string
            instance = self.objects[self.modelName]()
            instance.save()
            # This error may usually be KeyError
        except Exception as e:
            return {'success':False,'message':str(e)}
        else:
            # Now, let's use passed keyword arguments to set field values for our instance
            for key,val in kwargs.items():
                try:
                    main = self.modelName
                    if raltionship(self.objects[main],key) == "many_to_one":
                        # TODO: create new objects recersively from relations
                        try:
                            rel_name = getRelatedName(self.objects[main],key)
                            child_model = self.objects[rel_name]
                            children = child_model.objects.get(id=int(val))
                        except Exception as e:
                            pass
                            # return {'success':False,'message':str(e)}
                        else:
                            try:
                                instance.__setattr__(key,children)
                            except Exception as e:
                                return {'success':False,'message':str(e)}
                            else:
                                try:
                                    instance.save()
                                except Exception as e:
                                    return {'success':False,'message':str(e)}
                    # is the field a many to many key
                    elif raltionship(self.objects[self.modelName],key) == "many_to_many":
                        try:
                            rel_name = getRelatedName(self.objects[main],key)
                            child_model = self.objects[rel_name]
                            children = [child_model.objects.get(id=int(i)) for i in val]
                        except Exception as e:
                            return {'success':False,'message':str(e)}
                        else:
                            try:
                                # field = self.objects[self.modelName]._meta.get_field(key)
                                # field.set(children)
                                # instance.__setattr__(key,children)
                                # my_list = ['pharmacies', 'divisions']
                                if key == "drug_type":
                                    instance.drug_type.add(*children)

                                if key == "pharmacies":
                                    instance.pharmacies.add(*children)


                                if key == "categories":
                                    instance.categories.add(*children)

                                if key == "working_days":
                                    instance.working_days.add(*children)

                                if key == "work_days":
                                    instance.work_days.add(*children)

                                if key == "other_languages":
                                    instance.other_languages.add(*children)

                                if key == "recepients":
                                    instance.recepients.add(*children)

                                if key == "replies":
                                    instance.replies.add(*children)

                                if key == "other_languages":
                                    instance.other_languages.add(*children)

                                if key == "sourvenirs":
                                    instance.sourvenirs.add(*children)

                            except Exception as e:
                                return {'success':False,'message':str(e)}
                            else:
                                try:
                                    instance.save()
                                except Exception as e:
                                    return {'success':False,'message':str(e)}

                    else:
                        try:
                            instance.__setattr__(key,val)
                        except Exception as e:
                            return {'success':False,'message':str(e)}
                except:
                    pass
                    # # is the field a foreign key
                    # main = self.modelName
                    # if raltionship(self.objects[main],key) == "many_to_one":
                    #     # TODO: create new objects recersively from relations
                    #     try:
                    #         rel_name = getRelatedName(self.objects[main],key)
                    #         child_model = self.objects[rel_name]
                    #         children = child_model.objects.get(id=int(val))
                    #     except Exception as e:
                    #         return {'success':False,'message':str(e)}
                    #     try:
                    #         instance.__setattr__(key,children)
                    #     except Exception as e:
                    #         return {'success':False,'message':str(e)}
                    #     instance.save()
                    # # is the field a many to many key
                    # if raltionship(self.objects[self.modelName],key) == "many_to_many":
                    #     try:
                    #         rel_name = getRelatedName(self.objects[self.modelName],key)
                    #         child_model = self.objects[rel_name]
                    #         children = [child_model.objects.get(id=int(i)) for i in val]
                    #     except Exception as e:
                    #         return {'success':False,'message':str(e)}
                    #     instance.save()
                    # try:
                    #     instance.__setattr__(key,children)
                    # except Exception as e:
                    #     return {'success':False,'message':str(e)}
                    # instance.save()
                else:
                    instance.save()
                 # is the field a foreign key

            # try:
            #     instance.__setattr__(key,children)
            # except Exception as e:
            #     return {'success':False,'message':str(e)}
            # instance.save()
        # adding parents to the object (may be more than one parent
        # if parents:
        #     for parent in parents:
        #         try:
        #             parent = parent['name']
        #             instance.__setattr__(parent,parent['value'])
        #             instance.save()
        #         except:
        #             pass
        return {'success':True,'message':'successful','data':instance}

    # reads from database the particular model instance given
    # TODO: add specific field to be returned as **kwargs
    def read(self,key_id,primary_key,*fields):
        # setting the model based on passed model string
        # and getting all fields of the model
        allfields = self.objects[self.modelName]._meta.get_fields()
        # setting instance as passed instance
        arg = {key_id:primary_key}
        instance = self.objects[self.modelName].objects.get(**arg)
        names = []
        vals = []
        # here we get all the available fields on a particular instance
        # this means if the field is not yet created but exists on the model, it will not be taken
        objects = {}
        # This will use user defined field when return the object requested
        if fields:
            for field in fields:
                try:
                    val = (getattr(instance, field))
                except:
                    pass
                else:
                    names.append(field)
                    try:
                        obj = list(val.values())
                    except:
                        vals.append(val)
                    else:
                        vals.append(obj)
            for i,e in enumerate(names):
                objects[e]=vals[i]

        else:
            # this will return all available fields on the instance
            for field in allfields:
                try:
                    val = (getattr(instance, field.name))
                except:
                    pass
                else:
                    names.append(field.name)
                    try:
                        obj = list(val.values())
                    except:
                        vals.append(val)
                    else:
                        vals.append(obj)
            for i,e in enumerate(names):
                objects[e]=vals[i]
            # our return dictionary contains fields with their values even ManyToMany or related field
            # Already serialized
        dump = json.dumps(objects,cls=ExtendedEncoder)
        return {'success':True,'data':dump}

    # class method to update object
    def update(self,key_id,primary_key,**kwargs):
        try:
            arg = {key_id:primary_key}
            instance = self.objects[self.modelName].objects.get(**arg)
        except Exception as e:
            return {'success':False,'message':str(e)}
        else:
            for key,val in kwargs.items():
                try:
                    instance.__setattr__(key,val)
                except:
                    pass
            instance.save()
        # data = {'data':instance}
        # dump = json.dumps(data,cls=ExtendedEncoder)
        return {'success':True,'data':instance}


    # class method to delete instance of the model
    def delete(self,key_id,primary_key):
        try:
            arg = {key_id:primary_key}
            instance = self.objects[self.modelName].objects.get(**arg)
        except Exception as e:
            return False
        else:
            instance.delete()
            return {'success':True}



# utilities
class Generator:
    def __init__(self):
        pass

    def gen_request_no(self,number):
        if number > 0:
            no = str(number+1)
        else:
            no = str(1)
        return "#"+no.rjust(12, '0')

    def gen_sign(self,length):
        token = ''.join([choice('0123456789') for i in range(length)])
        return token


class Notify:
    def __init__(self):
        pass
    def email_users(self,users,email_subject,extra_args):
        for user in users:
            # username = user.username
            email = user.email
            extra_args['user']=user
            welcome_mail = Email.objects.get(subject=email_subject)
            email_html = open("/home/Learn/pharst/accounts/templates/welcome_email.html", "w+")
            email_txt = open("/home/Learn/pharst/accounts/templates/welcome_email.txt", "w+")
            email_html.write(welcome_mail.body)
            email_txt.write(welcome_mail.text)
            email_html.close()
            email_txt.close()
            msg_plain = render_to_string('welcome_email.txt',extra_args)

            msg_html = render_to_string('welcome_email.html', extra_args)
            subject = welcome_mail.subject
            send_mail(
            subject,
            msg_plain,
            'pythonwithellie@gmail.com',
            [email],
            html_message=msg_html,
            fail_silently=False,)


    def email_users_only_emails(self,emails,email_subject,extra_args):
        for email in emails:
            email = email
            welcome_mail = Email.objects.get(subject=email_subject)
            email_html = open("/home/Learn/pharst/accounts/templates/welcome_email.html", "w+")
            email_txt = open("/home/Learn/pharst/accounts/templates/welcome_email.txt", "w+")
            email_html.write(welcome_mail.body)
            email_txt.write(welcome_mail.text)
            email_html.close()
            email_txt.close()
            msg_plain = render_to_string('welcome_email.txt',extra_args)

            msg_html = render_to_string('welcome_email.html', extra_args)
            subject = welcome_mail.subject
            send_mail(
            subject,
            msg_plain,
            'pythonwithellie@gmail.com',
            [email],
            html_message=msg_html,
            fail_silently=False,)

    def fcm_notify(self,users,payload):
        for each in users:
            try:
                device = FCMDevice.objects.filter(user=each)[0]
            except:
                pass
            else:
                device.send_message(title=payload['title'], body=payload['body'], icon="https://pharst.pywe.org/static/Images/cell.png", data={"app": "pharst",'link':payload['link']})


    def send_sms(self,payload):
        phones = ""
        for i,c in enumerate(payload['phone']):
            if c.startswith("+") and len(c) == 13:
                phone = c.replace("+","",1)
            elif c.startswith("0") and len(c) == 10:
                # TODO: Remember to handle more countries here, let caller pass the country name in payload
                phone = c.replace("0","233",1)
            else:
                 phone = c
            if i == len(payload['phone'])-1:
                phones += str(phone)
            else:
                phones += str(phone) +","
        body = payload['body'].replace(" ","%20")
        url = "https://pushr.pywe.org/bulksender/send-sms-view/?username=Jidi&public_key=102f428795986859827e098a573d84&sender=Jidi&destination={}&message={}".format(phones,body)
        try:
            raw = r.get(url=url)
        except:
            pass
# mysqldump -h Learn.mysql.pythonanywhere-services.com 'Learn$pharst' -u Learn -p > pharst_new.sql