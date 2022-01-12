from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.
class Practice(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    image = models.FileField(upload_to="practices",null=True,blank=True)
    fee = models.FloatField(default=20)
    color = models.CharField(max_length=10,null=True,blank=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=14,null=True,blank=True)
    is_professional = models.BooleanField(default=False)
    notification_token = models.TextField(null=True,blank=True)
    otp = models.CharField(max_length=4,null=True,blank=True)
    user_image = models.FileField(upload_to="profiles",null=True,blank=True)
    about = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.username + " "+ str(self.id)

class Email(models.Model):
    pass


class Practitioner(CustomUser):
    practice = models.ForeignKey(Practice,null=True,on_delete=models.SET_NULL,related_name="professionals")
    location = models.CharField(max_length=100,null=True,blank=True,help_text="e.g Accra, Ghana")
    rating = models.FloatField(default=5.0)
    appointments = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class PracticeDocument(models.Model):
    practitioner = models.ForeignKey(Practitioner,null=True,on_delete=models.SET_NULL,related_name="documents")
    file = models.FileField(upload_to="practitioners_documents",null=True,blank=True)


class Patient(CustomUser):
    age = models.IntegerField(default=20)


    def __str__(self):
        return self.username


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank = True, on_delete = models.CASCADE)
    topup_account = models.FloatField(default=00.0,null=True)
    service_account = models.FloatField(default=00.0,null=True)
    last_recharged = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    exp_date = models.DateTimeField(null=True)
    last_transid = models.CharField(max_length=12,null=True,blank=True)
    cumulative_bal = models.FloatField(default=00.0,null=True)


    def __str__(self):
        return self.user.username

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=20,null=True)
    transaction_type = models.CharField(max_length=20,null=True)
    order_id = models.CharField(max_length=50,null=True,blank=True)
    status = models.CharField(max_length=20,null=True)
    completed = models.BooleanField(default=False)
    amount = models.FloatField(default=0.0)
    account = models.CharField(max_length=30,null=True)
    date_created = models.DateTimeField(null=True,auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank = True, on_delete = models.SET_NULL,related_name="transactions")

    def __str__(self):
        return self.transaction_id

