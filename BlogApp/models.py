

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# class Register(models.Model):

#     username = models.CharField(max_length=100)
#     firstname = models.CharField(max_length=100)
#     lastname = models.CharField(max_length=100)
#     email = models.EmailField()
#     contact = models.CharField(max_length=20,blank=True, null=True)
#     password = models.CharField(max_length=100) 
#     password1 = models.CharField(max_length=100)
#     image=models.ImageField(upload_to='blog_media')
   

#     def __str__(self):
#         return '{}'.format(self.username)
ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
                    ]

class Usertable(models.Model):
   
    username=models.CharField(max_length=200,unique=True)
    firstname=models.CharField(max_length=200)
    lastname=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    contact = models.CharField(max_length=20, blank=True, null=True)
    password=models.CharField(max_length=200)
    image=models.ImageField(upload_to='blog_media')
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)

    def __str__(self):
        return '{}'.format(self.username)
    

class logintable(models.Model):
    
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    

    def __str__(self):
        return '{}'.format(self.username)

class Blog(models.Model):
    owner = models.ForeignKey(logintable, on_delete=models.CASCADE)  
    title = models.CharField(max_length=200)
    description = models.TextField()
    image=models.ImageField(upload_to='blog_media')
    owner = models.ForeignKey(logintable, on_delete=models.CASCADE, related_name='blogs',null=True)
   
    

    def __str__(self):
        return '{}'.format(self.title)




class Comment(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    user = models.ForeignKey('logintable', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.blog.title}'