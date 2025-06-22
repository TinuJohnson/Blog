
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
        
        # Check if passwords match
        if password != password1:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        user_role = request.POST.get('type', 'user')
        
        # Create user
        userprofile = Usertable(
            username=request.POST['username'],
            password=request.POST['password'],  # Hash the password
            role=request.user_role, # Changed from 'role' to 'type'
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            email=request.POST['email'],
            contact=request.POST.get('contact'),
            image=request.FILES.get('profilepic')  # Changed from 'image' to 'profilepic'
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
        role = 'user'  # Default role

        try:
            user_details = logintable.objects.get(username=username)
            
            # Check if password matches
            if user_details.password == password:  # In production, use check_password()
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
    # Check if user is logged in
    if 'username' not in request.session:
        return redirect('login')
    
    try:
        # Get the user object from the database
        user = logintable.objects.get(username=request.session['username'])
        
        # Filter blogs by the user instance (not by username string)
        blogs = Blog.objects.filter(owner=user)
        image = Usertable.objects.all()
        
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
    # Check session instead of using @login_required
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

        # Handle password update
        new_password = request.POST.get('password')
        if new_password:
            profile.password = new_password  # You should hash it if using for real auth

        # Handle profile image update
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
