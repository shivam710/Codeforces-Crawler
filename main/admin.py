from django.contrib import admin
from .models import *

admin.site.register(languages)
admin.site.register(verdicts)
admin.site.register(levels)
admin.site.register(Chatmessage)
admin.site.register(Chatroom)