
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from .models import Blog,Usertable,Comment,logintable
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError


 
def useRegistration(request):
    if request.method == 'POST':
        password = request.POST['password']
        password1 = request.POST['password1']
        
      
        if password != password1:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        user_role = request.POST.get('type', 'user')
        
        # Create user
        userprofile = Usertable(
            username=request.POST['username'],
            password=request.POST['password'],  
            role=request.user_role,
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            email=request.POST['email'],
            contact=request.POST.get('contact'),
            image=request.FILES.get('profilepic') 
        )

        loginprofile = logintable(
            username=request.POST['username'],
            password=request.POST['password'],
            is_admin=(user_role == 'admin') 
            
        )
        
        try:
            userprofile.save()
            loginprofile.save()
            messages.success(request, 'Registration successful')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('register')

    return render(request, 'register.html')

def login1(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = 'user' 
        try:
            user_details = logintable.objects.get(username=username)
            
            
            if user_details.password == password:  
                request.session['username'] = user_details.username
                
                if role == 'user':
                    return redirect('home')
                elif role == 'admin':
                    return redirect('admin')
            else:
                messages.error(request, 'Incorrect password')
                
        except logintable.DoesNotExist:
            messages.error(request, 'Username does not exist')
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')

    return render(request, 'login.html')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            user = Usertable.objects.get(username=username)
            request.session['reset_user_id'] = user.id
            return redirect('set_new_password')
        except Usertable.DoesNotExist:
            messages.error(request, 'Username does not exist')
            return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')

def set_new_password(request):
    if 'reset_user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['reset_user_id']
    
    try:
        user = Usertable.objects.get(id=user_id)
    except Usertable.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords don't match")
            return redirect('set_new_password')
        
        try:
         
            hashed_password = make_password(new_password)
            
         
            user.password = hashed_password
            user.save()
            
           
            try:
                login_record = logintable.objects.get(username=user.username)
                login_record.password = new_password
                login_record.save()
            except logintable.DoesNotExist:
             
                logintable.objects.create(
                    username=user.username,
                    password=hashed_password
                )
           
            del request.session['reset_user_id']
            
            messages.success(request, 'Password updated successfully!')
            return redirect('login')
        
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
    
    return render(request, 'set_new_password.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


def blog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        img = request.FILES.get('image')

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
 
    if 'username' not in request.session:
        return redirect('login')
    
    try:
    
        user = logintable.objects.get(username=request.session['username'])
        
        blogs = Blog.objects.filter(owner=user)
     
        
        context = {
            'blogs': blogs,
            'username': request.session['username'],
            
        }
        return render(request, 'my_blogs.html', context)
        
    except logintable.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')


def listblog(request):

    blogs=Blog.objects.all()
    
    paginator=Paginator(blogs,4)
    page_number=request.GET.get('page')
    
    try:
        page=paginator.get_page(page_number)
        
    except EmptyPage:
        page=paginator.page(page_number.num_pages)
        

    return render(request,'home.html',{'blogs':blogs,'page':page})








def user_profile(request):
   
    if 'username' not in request.session:
        return redirect('login')
    
    try:
        username = request.session['username']
        profile = Usertable.objects.get(username=username)
        return render(request, 'profile.html', {'profile': profile})
        
    except Usertable.DoesNotExist:
        messages.info(request, "Please complete your profile first")
        return redirect('edit_profile')



def edit_profile(request):
    if 'username' not in request.session:
        messages.error(request, 'Please login to edit profile')
        return redirect('login')
    print("Current user in session:", request.session.get('username'))


    try:
        username = request.session['username']
        profile = Usertable.objects.get(username=username)
    except Usertable.DoesNotExist:
        messages.error(request, "Profile not found")
        return redirect('login')


    if request.method == 'POST':
        profile.firstname = request.POST.get('firstname', profile.firstname)
        profile.lastname = request.POST.get('lastname', profile.lastname)
        profile.email = request.POST.get('email', profile.email)
        profile.contact = request.POST.get('contact', profile.contact)

        new_password = request.POST.get('password')
        if new_password:
            profile.password = new_password  

       
        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        try:
            profile.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('user_profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    return render(request, 'edit_profile.html', {'profile': profile})




def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog_list.html', {'blogs': blogs})

def add_comment(request, blog_id):
  
    if 'username' not in request.session:
        messages.error(request, 'Please login to comment')
        return redirect('login')
     
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == 'POST':
        text = request.POST.get('comment_text', '').strip()
        
        if not text:
            messages.error(request, 'Comment cannot be empty')
        else:
            try:
                user = logintable.objects.get(username=request.session['username'])
  
                Comment.objects.create(
                    blog=blog,
                    user=user, 
                    text=text
                )
                messages.success(request, 'Comment added successfully')
            except Usertable.DoesNotExist:
                messages.error(request, 'User not found')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error adding comment: {str(e)}')

    return redirect('blog_detail', blog_id=blog.id)




def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog, 'username': request.session.get('username')})



def edit_blog(request, blog_id):
    if 'username' not in request.session:
        return redirect('login')

    blog = get_object_or_404(Blog, id=blog_id)
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.description = request.POST.get('description')
        if 'image' in request.FILES:
            blog.image = request.FILES['image']
        blog.save()
        return redirect('my-blogs')

    return render(request, 'edit_blog.html', {'blog': blog})


def delete_blog(request, blog_id):
    if 'username' not in request.session:
        return redirect('login')
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        blog.delete()
        return redirect('my-blogs')
    
    
def search(request):
    Query=None
    blogs=None

    if 'q' in request.GET:

        Query=request.GET.get('q')
        blogs=Blog.objects.filter(Q(title__icontains=Query))

    else:
        blogs=[]


    context={'blogs':blogs,'Query':Query}

    return render(request,'search.html',context)

def edit_comment(request, comment_id):
    if 'username' not in request.session:
        return redirect('login')

    comment = get_object_or_404(Comment, id=comment_id)
    username = request.session['username']

    if comment.user.username != username:
        messages.error(request, "You can only edit your own comments.")
        return redirect('blog_detail', blog_id=comment.blog.id)

    if request.method == 'POST':
        new_text = request.POST.get('comment_text', '').strip()
        if new_text:
            comment.text = new_text
            comment.save()
            messages.success(request, "Comment updated successfully.")
        else:
            messages.error(request, "Comment cannot be empty.")
        return redirect('blog_detail', blog_id=comment.blog.id)

    return render(request, 'edit_comment.html', {'comment': comment})

def delete_comment(request, comment_id):
    if 'username' not in request.session:
        return redirect('login')

    comment = get_object_or_404(Comment, id=comment_id)
    username = request.session['username']

    if comment.user.username != username:
        messages.error(request, "You can only delete your own comments.")
        return redirect('blog_detail', blog_id=comment.blog.id)

    if request.method == 'POST':
        blog_id = comment.blog.id
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('blog_detail', blog_id=blog_id)

    return render(request, 'confirm_delete_comment.html', {'comment': comment})
