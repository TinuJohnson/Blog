import profile
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from .models import Blog,Userprofile,logintable,Comment
from django.db.models import Q
from django.contrib.auth.decorators import login_required

 # Import your Register model

# Create your views here
# def Register(request):
    
#     if request.method=='POST':

#         username=request.POST.get('username')
#         firstname=request.POST.get('firstname')
#         lastname=request.POST.get('lastname')
#         email=request.POST.get('email')
#         contact=request.POST.get('contactnumber')
#         password=request.POST.get('password')
#         password1=request.POST.get('password1')
      

#         if password==password1:
#             if User.objects.filter(username=username).exists():
#                 messages.info(request,'This username is alredy exixts')
#                 return redirect('register')
#             elif User.objects.filter(email=email).exists():
#                 messages.info(request,'This email is alredy registered')
#                 return redirect('register')
#             else:
#                 user=User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password)
#                 user.save()
                
#                 return redirect('login')
        
#         else:
#             messages.info(request,'This password is not matching')
#             return redirect('register')


#     return render(request,'register.html')







# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username', '').strip()
#         password = request.POST.get('password', '').strip()
        
#         # Basic validation
#         if not username or not password:
#             messages.error(request, 'Both username and password are required')
#             return redirect('login')
        
#         try:
#             # Check if user exists in Register model
#             user_record = Register.objects.get(username=username)
            
#             # Verify password (Note: This is insecure if passwords are stored plaintext)
#             if user_record.password == password:
#                 # Create session or mark user as logged in
#                 request.session['user_id'] = user_record.id
#                 request.session['username'] = user_record.username
#                 messages.success(request, 'Login successful!')
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Invalid password')
#                 return redirect('login')
                
#         except Register.DoesNotExist:
#             messages.error(request, 'Username does not exist')
#             return redirect('login')
    
#     return render(request, 'login.html')

# def register(request):

#      if request.method=='POST':
       
#         username=request.POST.get('username')
#         firstname=request.POST.get('firstname')
#         lastname=request.POST.get('lastname')
#         email=request.POST.get('email')
#         contact=request.POST.get('contact')
#         password=request.POST.get('password')
#         password1=request.POST.get('password1')
#         image=request.FILES.get('image')

        
        
      

#         if password==password1:
#             if Register.objects.filter(username=username).exists():
#                 messages.info(request,'This username is alredy exixts')
#                 return redirect('register')
#             elif Register.objects.filter(email=email).exists():
#                 messages.info(request,'This email is alredy registered')
#                 return redirect('register')
#             else:
#                 users=Register(username=username,firstname=firstname,lastname=lastname,email=email,password=password,contact=contact,image=image)
#                 users.save()
#                 return redirect('login')

#         else:
#             messages.info(request,'This password is not matching')
#             return redirect('register')
        
    
#      return render(request,'register.html')
    
def useRegistration(request):
    login_table=logintable()
    userprofile=Userprofile()

    if request.method=='POST':
        userprofile.username=request.POST['username']
        userprofile.password=request.POST['password']
        userprofile.password1=request.POST['password1']
        userprofile.firstname=request.POST['firstname']
        userprofile.lastname=request.POST['lastname']
        userprofile.email=request.POST['email']
        userprofile.contact=request.POST.get('contact')
        userprofile.image=request.FILES.get('image')

        login_table.username=request.POST['username']
        login_table.password=request.POST['password']
        login_table.password1=request.POST['password1']
        login_table.type='user'

        if request.POST['password']==request.POST["password1"]:
            userprofile.save()
            login_table.save()

            messages.info(request,'Registration is sucessfull')
            return redirect('login')
        
        else:
            messages.info(request,'Password is not matching')
            return redirect('register')

    return render(request,'register.html')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=logintable.objects.filter(username=username,password=password,type='user').exists()
        try:

            if user is not None:

                user_details=logintable.objects.get(username=username,password=password)
                user_name=user_details.username
                type=user_details.type

                if type=='user':
                    request.session['username']=user_name
                    return redirect('home')
                elif type=='admin':
                    request.session['username']=user_name
                    return redirect('admin')
            else:
                messages.error(request,'Invalid user')   

        except:
            messages.error(request,'Invalid role')

    return render(request,'login.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


def blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        img = request.FILES.get('image')

        # Get current logged-in user from session
        username = request.session.get('username')
        try:
            user = logintable.objects.get(username=username)
        except logintable.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('login')

        blog = Blog(title=title, description=desc, image=img, owner=user)
        blog.save()
        return redirect('home')

    return render(request, 'create.html')

def my_blogs(request):
    username = request.session.get('username')
    user = logintable.objects.get(username=username)
    blogs = Blog.objects.filter(owner=user)
    return render(request, 'my_blogs.html', {'blogs': blogs})

def listblog(request):

    blogs=Blog.objects.all()

    return render(request,'home.html',{'blogs':blogs})


from django.contrib.auth.decorators import login_required


def user_profile(request):
    try:
        profile = Userprofile.objects.get(username=request.user.username)
    except Userprofile.DoesNotExist:
        # Redirect to edit profile if doesn't exist
        messages.info(request, "Please complete your profile first")
        return redirect('edit_profile')
    
    return render(request, 'profile.html', {'profile': profile})



def edit_profile(request):
    try:
        # Try to get the user's profile
        profile = Userprofile.objects.get(username=request.user.username)
    except Userprofile.DoesNotExist:
        # If profile doesn't exist, create a new one
        profile = Userprofile.objects.create(
            username=request.user.username,
            firstname=request.user.first_name if hasattr(request.user, 'first_name') else '',
            lastname=request.user.last_name if hasattr(request.user, 'last_name') else '',
            email=request.user.email if hasattr(request.user, 'email') else ''
        )
        messages.info(request, "Created a new profile for you")

    if request.method == 'POST':
        # Update profile fields
        profile.firstname = request.POST.get('firstname', profile.firstname)
        profile.lastname = request.POST.get('lastname', profile.lastname)
        profile.email = request.POST.get('email', profile.email)
        profile.contact = request.POST.get('contact', profile.contact)
        
        # Handle image upload
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        
        # Save the updated profile
        profile.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('user_profile')
    
    return render(request, 'edit_profile.html', {'profile': profile})
       




from .models import Blog, Comment

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog_list.html', {'blogs': blogs})

def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, izd=blog_id)
    if request.method == 'POST':
        text = request.POST.get('comment_text', '').strip()
        if text:
            username = request.session['username']
            user = logintable.objects.get(username=username)
            Comment.objects.create(
                blog=blog,
                user=user,
                text=text
            )
    return redirect('blog_detail', blog_id=blog.id)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})



# def search(request):
#     Query=None
#     blogs=None

    if 'Q' in request.GET:

        Query=request.GET.get('Q')
        blogs=Blog.objects.filter(Q(title__icontains=Query))

    else:
        blogs=[]


    context={'blogs':blogs,'Query':Query}

    return render(request,'search.html',context)