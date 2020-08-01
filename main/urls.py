from django.urls import path
from . import views as v
from users import views as v1
from django.conf.urls import url


app_name='main'

urlpatterns = [
    path('', v.home, name='home'),
    path('cfhandle/', v.cfhandle, name="cfhandle"),
    path('cfhandle/<str:handle>', v.who, name='who'),
    path('timetable/', v.time_table, name="time_table"),
    path('timetable/codeforces', v.code_forces, name="code_forces"),
    path('timetable/codechef', v.code_chef, name="code_chef"),
    path('contest/<str:handle>', v.contest, name='contest-statistics'),
    path('contact/', v.contact, name='contact'),
    path('iitg/', v.iitg, name='iitg'),
    path('allchat/', v.allchat, name='allchat'),
    path('chatroom/<str:userid1>/<str:userid2>/', v.chatroom, name='chatroom'),
]
