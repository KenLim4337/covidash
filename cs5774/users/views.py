from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import resolve
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from actions.models import Action

def profile(request, username):
    tempuser = get_object_or_404(User, username__iexact=username)
    actions = Action.objects.filter(user=tempuser).order_by('-date')[:20]

    return render(request, 'users/profile.html', {
        'userdata': tempuser,
        'actions': actions
    })

def register(request):
     #if form submitted
    if request.method == 'POST':
        addName = request.POST.get("username")
        addFName = request.POST.get("firstname")
        addLName = request.POST.get("lastname")

        #always store emails in lowercase
        addEmail = request.POST.get("email").lower()
        addPass = request.POST.get("password")

        #Prevent username dupes as it is used for urls
        if(User.objects.filter(username__iexact = addName).count() > 0):
            messages.add_message(request, messages.WARNING, "Username: %s already taken" % addName)
            return redirect('users:register')

        #Prevent email dupes as it is used for urls
        if(User.objects.filter(email__iexact = addEmail).count() > 0):
            messages.add_message(request, messages.WARNING, "Email: %s is already in use" % addEmail)
            return redirect('users:register')

        #Add cart items to the user's dashboard
        user = User.objects.create_user(addName,addEmail,addPass)

        user.first_name = addFName
        user.last_name = addLName

        user.save()

        #message for testing. replace with db code in next project
        messages.add_message(request, messages.SUCCESS, "Welcome to CoviDash %s!" % user.username)

        #Also log the user in
        request.session['username'] = user.username
        request.session['role'] = user.details.role
        request.session['userid'] = user.pk

        return redirect('coviDash:home')

    return render(request, 'users/register.html')

def edit_user(request, username):     
    if request.session.get('username').lower() == username.lower() or request.session.get('role') == 'admin' or request.session.get('role') == 'developer':

        #Get user
        user = User.objects.get(username__iexact=username)
            
        #If form submit
        if request.method == 'POST':
            editName = request.POST.get("username")
            editFName = request.POST.get("firstname")
            editLName = request.POST.get("lastname")

            editEmail = request.POST.get("email")
            editPass = request.POST.get("password")
            oldPass = request.POST.get("oldpassword")
            editRole = request.POST.get("makeadmin")

            #Check match old password before going forward
            
            
            if editName: 
                user.username = editName

            
            if editFName: 
                user.first_name = editFName

            
            if editLName: 
                user.last_name = editLName

            if editEmail: 
                user.email = editEmail.lower()

            if editPass: 
                if not user.check_password(oldPass):
                    messages.add_message(request, messages.WARNING, "Old password does not match current password")
                    return redirect('users:edit-user', username=user.username.lower())
                user.set_password(editPass)

            if editRole == "admin": 
                user.details.make_admin()

                activityLog = Action(
                    user = user,
                    verb = "UP"
                )

                activityLog.save()

                messages.add_message(request, messages.SUCCESS, "%s made into an Admin!" % user.username)
            elif editRole == "regular": 
                user.details.strip_admin()
                
                activityLog = Action(
                    user = user,
                    verb = "DP"
                )

                activityLog.save()

                messages.add_message(request, messages.SUCCESS, "%s removed as an Admin!" % user.username)

            user.save()
            user.details.save()
            
            #Update session to reflect new information if the edit matches the logged in user
            if(user.id == request.session['userid']):
                request.session['username'] = user.username
                request.session['role'] = user.details.role
                request.session['userid'] = user.pk

            messages.add_message(request, messages.SUCCESS, "Changes to the account have been successfully saved!")
            
            #Back to user's profile after edit or admin page
            if "admin" in request.META.get('HTTP_REFERER'):
                return redirect('coviDash:admin')
            else:
                return redirect('users:profile', username=user.username.lower())


        #Otherwise display form
        return render(request, 'users/register.html', {
            'userdata': user
        })

    else: 
        #Boot people away if not admin or appropriate user
        return redirect('coviDash:home')

def remove_user(request):
    #get posted stuff
    removeId = request.POST.get("userId")

    user = User.objects.get(pk=removeId)

    username = user.username

    user.delete()

    #make success message for testing. replace with actual remove stuff in next project
    messages.add_message(request, messages.WARNING, "You have successfully removed user " + str(username))

    return redirect('coviDash:home')


def login_user(request):
    if request.method == 'POST':
        #get posted variables
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(username = username, password = password)

        if user is not None: 
            request.session['username'] = user.username
            request.session['role'] = user.details.role
            request.session['userid'] = user.pk
            messages.add_message(request, messages.SUCCESS, "Welcome back %s!" % user.username)

            #Redirect back to home page
            return redirect('coviDash:home')

        else:
            messages.add_message(request, messages.WARNING, "Invalid username or password")
            return redirect('users:login')

    #Redirect to login
    return render(request, 'users/login.html')

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
