from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Post, Profile
from .forms import PostForm, UserRegisterForm, CommentForm # Add CommentForm here
from django.urls import reverse


# 1. GUEST FRIENDLY: Anyone can view the board
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'board/home.html', {'posts': posts})

# 2. PROTECTED: Create a new post
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'board/create_post.html', {'form': form})

# 3. PROTECTED: Toggle Likes
@login_required
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    # Toggle the like
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    # Get the scroll position from the POST data
    scroll_pos = request.POST.get('scroll_pos', '0')
    
    # Redirect back to home with the scroll value in the URL
    return redirect(f"{reverse('home')}?scroll={scroll_pos}")
# 4. Registration (The missing piece!)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            
            # Update the profile (created by signal) with the pic
            profile_pic = form.cleaned_data.get('profile_pic')
            if profile_pic:
                user.profile.profile_pic = profile_pic
                user.profile.save()
            
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'board/register.html', {'form': form})




@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Keep the scroll position
            scroll_pos = request.POST.get('scroll_pos', '0')
            return redirect(f"{reverse('home')}?scroll={scroll_pos}")
    return redirect('home')

def home(request):
    # 1. Fetch all posts to show on the board
    posts = Post.objects.all().order_by('-created_at')
    
    # 2. Create an empty instance of the form (Step 4)
    comment_form = CommentForm() 
    
    # 3. Pass both to the template
    return render(request, 'board/home.html', {
        'posts': posts,
        'comment_form': comment_form 
    })