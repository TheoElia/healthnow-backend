from django.conf.urls import url
from . import views


urlpatterns = [
    # url(r'^$', views.index,name="home"),
    url(r'^api/v1/accounts/create-user/$', views.registerUser,name="create-user"),
    url(r'^api/v1/accounts/create-professional/$', views.registerProfessional,name="create-professional"),
    url(r'^api/v1/accounts/login-user/$', views.loginUser,name="login-user"),
    url(r'^api/v1/accounts/get-user/$', views.getUser,name="get-user"),
    url(r'^accounts/get-transactions/$', views.getTransactions,name="get-transactions"),
    url(r'^api/v1/accounts/charge-user/$', views.chargeUser,name="charge-user"),
    url(r'^api/v1/system/verify-payment/$', views.verifyTopup,name="verify-topup"),
    url(r'^accounts/topup/(?P<email>[-\w]+)/$', views.make_payment,name="topup"),
]
