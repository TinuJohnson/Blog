from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("", views.useRegistration, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('blog/create/', views.blog, name='create'),
    path('home/', views.listblog, name='home'),
    path('my-blogs/', views.my_blogs, name='my-blogs'),
    path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),



]




