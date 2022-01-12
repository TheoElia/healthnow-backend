from django.db import models
from django.conf import settings

# Create your models here.
class Request(models.Model):
    message = models.TextField(null=True)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="requests")
    professional = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="my_requests")
    time_created = models.DateTimeField(auto_now_add=True)
    consultation_fee = models.FloatField(default=20)
    paid = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    attended_to = models.BooleanField(default=False)
    appointment_date = models.DateTimeField(null=True,blank=True)
    meeting_link = models.CharField(max_length=200,null=True,blank=True)
    professional_comments = models.TextField(null=True,blank=True)
    rating = models.IntegerField(default=1)
    feedback = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=15,null=True,blank=True,default="pending")


    def __str__(self):
        return self.message


class Message(models.Model):
    message = models.TextField(null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="sender")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="receiver")
    # reply = models.ForeignKey("self",null=True, blank = True, on_delete = models.SET_NULL)

    def __str__(self):
        return self.sender.username

