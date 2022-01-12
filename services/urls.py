from django.conf.urls import url,include
from . import views


urlpatterns = [
    # url(r"^api/v1/fixers/search-fixer/$",views.fetchFixers, name="fetch-fixers"),
    url(r"^api/v1/services/search-by-category/$",views.fetchbyCategory, name="fetch-by-category"),
    url(r"^api/v1/services/create-request/$",views.createRequest, name="create-request"),
    url(r"^api/v1/services/rate-professional/$",views.rateProfessional, name="rate-professional"),
    url(r"^api/v1/services/update-request/$",views.updateRequest, name="update-request"),
    url(r"^api/v1/services/fetch-all-categories/$",views.fetchAllCategories, name="fetch-all-categories"),
    url(r"^api/v1/services/get-requests/$",views.getRequests, name="get-requests"),
     url(r"^api/v1/services/create-message/$",views.createMessage, name="create-message"),
     url(r"^api/v1/services/read-message/$",views.readMessage, name="read-message"),
    # url(r"^api/v1/publications/(?P<id>[^/]+)/$",views.customer_persona, name="customer-persona"),
]