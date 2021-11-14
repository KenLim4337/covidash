from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import resolve
from django.http import JsonResponse
from .models import Rumour
from actions.models import Action
from django.contrib.auth.models import User
from django.core import serializers

def home(request):
    #pass detailed user data if logged in for dashboard otherwise empty userData will be passed
    if request.session.get('userid', None) != None:
        tempUser = User.objects.get(pk=request.session.get('userid', None))

        #Newest first, limit to 20 items
        actions = Action.objects.all().order_by('-date')[:20]

        userData = {
            #mess around with added later
            'added': [1,2,3,4],
            'posted': tempUser.details.posted,
            'cited': tempUser.details.cited,
            'solved': tempUser.details.solved,
            'title': tempUser.details.title
        }

        return render(request, 'coviDash/home.html', {
            'rumours': Rumour.objects.all().order_by('pk'),
            'userData': userData,
            'actions': actions
        })
    else: 
        return render(request, 'coviDash/home.html',{
            'rumours': Rumour.objects.all().order_by('pk')
        })


def cart(request):
    return render(request, 'coviDash/cart.html',{
        'rumours': Rumour.objects.all(),
    })

def list(request):
    #default sort (recent aka highest ID first)
    sortQ = '-pk'

    #Translate human-readable into actual queries
    sortQueries = {
        'newest': '-id',
        'oldest': 'id',
        'a-z': 'title',
        'z-a': '-title',
        'validity': '-validity',
        'poster': '-poster',
    }

    if request.method == "GET" and request.GET.get('sortby'):
    #fiddle with sort if sorting is present
        sortQ = sortQueries[request.GET.get('sortby')]

    #Default list to passthrough: listing page
    resultRumours = Rumour.objects.order_by(sortQ)

    #Handle search if search
    if resolve(request.path_info).url_name == "search" and request.GET.get('searchquery'):
        #query based on query
        query = request.GET.get('searchquery')
        resultRumours = Rumour.objects.filter(
            title__icontains=query
        )|Rumour.objects.filter(
            description__icontains=query
        )|Rumour.objects.filter(
            bodyHtml__icontains=query
        )|Rumour.objects.filter(
            poster__icontains=query
        ).order_by(sortQ)

    return render(request, 'coviDash/list.html', {
        'rumours': resultRumours
    })

def detail(request, rumour_id):
    #Check for id in list
    rumour = Rumour.objects.get(pk=rumour_id)

    return render(request, 'coviDash/detail.html', {
        'rumour': rumour
    })

def add(request):
    #check if user is logged in. if no send back to home
    if request.session.get('userid', None) == None:
        return redirect('coviDash:home')

    #if form submitted
    if request.method == 'POST':
        addTitle = request.POST.get("title")
        addDesc = request.POST.get("description")
        addBody = request.POST.get("bodytext")
        addImg = request.POST.get("picture")

        newRumour = Rumour(
            title = addTitle,
            description = addDesc,
            bodyHtml = addBody,
            img = addImg,
            poster = User.objects.get(pk=request.session.get('userid'))
        )

        newRumour.save()

        activityLog = Action(
            user = User.objects.get(pk=request.session.get('userid')),
            verb = "added a rumour",
            target = newRumour,
        )

        activityLog.save()

        #message for testing. replace with db code in next project
        messages.add_message(request, messages.SUCCESS, "You have successfully added the rumour: " + request.POST.get("title") + " - " + request.POST.get("description"))

        return redirect('coviDash:rumour-detail', rumour_id=Rumour.objects.last().id)

    #Show form
    return render(request, 'coviDash/add.html')


def edit(request, rumour_id):
    #Get rumour from objects
    rumour = Rumour.objects.get(pk=rumour_id)

    #check if user is logged in. if no send back to home
    if request.session.get('userid', None) == None:
        return redirect('coviDash:home')

    #if form submitted
    if request.method == 'POST':
        #pull post variables
        editTitle = request.POST.get("title")
        editDesc = request.POST.get("description")
        editBody = request.POST.get("bodytext")
        editImg = request.POST.get("picture")

        rumour.title = editTitle
        rumour.description = editDesc
        rumour.bodyHtml = editBody
        rumour.img = editImg

        rumour.save()

        #message for testing. replace with db code in next project
        messages.add_message(request, messages.INFO, "You have successfully edited the rumour: " + editTitle + " - " + editDesc)

        #back whence you came
        return redirect('coviDash:rumour-detail', rumour_id=rumour_id)
    

    #Show form
    return render(request, 'coviDash/add.html', {
        'rumour': rumour
    })

def delete(request):
    #get posted stuff
    removeId = request.POST.get("rumourId")

    rumour = Rumour.objects.get(pk=removeId)

    rumour.delete()

    #make success message for testing. replace with actual remove stuff in next project
    messages.add_message(request, messages.WARNING, "You have successfully removed rumour " + str(removeId))

    #Sends user back to admin page
    return redirect('coviDash:admin')

def vote(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax and request.method == "POST":
        rumourId = request.POST.get('id')
        validity = request.POST.get('validity')

        try:
            rumour = Rumour.objects.get(pk=rumourId)
            
            if validity == "true": 
                #True
                rumour.verusersT += 1

            elif validity == "false": 
                #False
                rumour.verusersF += 1

            #Update total for other uses
            rumour.verusers = rumour.verusersT + rumour.verusersF

            #Calculate ratio and update validity
            fpercent = (rumour.verusersF/(rumour.verusersT+rumour.verusersF)) * 100;

            #More than 10 comments before tweaking validity
            if rumour.verusers > 10: 
                #More than 60% false = false (% are arbitrary)
                if fpercent > 60:
                    rumour.validity = "False"
                #Less than 40% false = true
                elif fpercent < 40:
                    rumour.validity = "True"
                #Otherwise = true
                else:
                    rumour.validity = "Mixed"
                    
            #save to db
            rumour.save()

            return JsonResponse({
                'success': 'success', 
                'true': rumour.verusersT,
                'false': rumour.verusersF,
                'validity': rumour.validity
            }, status=200)

        except Rumour.DoesNotExist:
            return JsonResponse({'error': 'No rumour found'}, status=200)

    else: 
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
def rumourget(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax and request.method == "POST":
        if request.POST.getlist('cartData[]'):
            cart = request.POST.getlist('cartData[]')
        elif request.POST.get('prodId'):
            cart = request.POST.get('prodId')

        try:
            #Query DB
            cartData = serializers.serialize("json", Rumour.objects.filter(id__in=cart))

            return JsonResponse({
                'success': 'success', 
                'results': cartData
            }, status=200)

        except Rumour.DoesNotExist:
            return JsonResponse({'error': 'No rumour found'}, status=200)

    else: 
        return JsonResponse({'error': 'Invalid request'}, status=400)