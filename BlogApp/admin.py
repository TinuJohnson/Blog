from django.contrib import admin
from .models import Blog,logintable,Userprofile,Comment
# Register your models here.
admin.site.register(Blog)
admin.site.register(logintable)
admin.site.register(Userprofile)
admin.site.register(Comment)