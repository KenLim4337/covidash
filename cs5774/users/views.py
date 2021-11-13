from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import resolve
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

titleList = {
    0: "Amateur Sleuth",
    10: "Novice Investigator",
    20: ""
}

def profile(request, username):
    tempuser = get_object_or_404(User, username__iexact=username)

    return render(request, 'users/profile.html', {
        'user': tempuser
    })

def register(request):
     #if form submitted
    if request.method == 'POST':
        addName = request.POST.get("username")
        #always store emails in lowercase
        addEmail = request.POST.get("email").lower()
        addPass = request.POST.get("password")

        #Add cart items to the user's dashboard
        user = User.objects.create_user(addName,addEmail,addPass)

        #message for testing. replace with db code in next project
        messages.add_message(request, messages.SUCCESS, "Welcome to CoviDash %s!" % user.username)

        #Also log the user in
        request.session['username'] = user.username
        request.session['role'] = user.details.role
        request.session['userid'] = user.pk

        return redirect('coviDash:home')

    return render(request, 'users/register.html')

def login_user(request):
    #get posted variables
    username = request.POST.get("username")
    password = request.POST.get("password")
    
    user = authenticate(username = username, password = password)

    if user is not None: 
        request.session['username'] = user.username
        request.session['role'] = user.details.role
        request.session['userid'] = user.pk
        messages.add_message(request, messages.SUCCESS, "Welcome back %s!" % user.username)
    else:
        messages.add_message(request, messages.ERROR, "Invalid username or password")

        #Redirect back to login page
        return redirect('coviDash:home')

    #Redirect to home
    return redirect('coviDash:home')

def logout_user(request):
    #try catch in case some weird stuff happens and user reaches logout link without actually being logged in
    try:
    #remove sesssion variables
        del request.session['username']
        del request.session['role']
        del request.session['userid']
    except KeyError:
        print('Key not set')

    #Always redirect back to home on logout
    return redirect('coviDash:home')
