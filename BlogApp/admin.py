from django.contrib import admin
from .models import Blog,logintable,Usertable,Comment
# Register your models here.
admin.site.register(Blog)
admin.site.register(logintable)
admin.site.register(Usertable)
admin.site.register(Comment)