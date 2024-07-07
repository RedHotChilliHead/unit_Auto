from django.urls import path
from .views import AccordanceApiView, AccordanceRedirect, AccordanceCreateView, AccordanceListView

app_name = "bitlyapp"

urlpatterns = [
    path('', AccordanceApiView.as_view(), name='accordance'),
    path('create/', AccordanceCreateView.as_view(), name='accordance-create'),
    path('list/', AccordanceListView.as_view(), name='accordance-list'),
    path('<str:short_url>/', AccordanceRedirect.as_view(), name='accordance-redirect'),
]
