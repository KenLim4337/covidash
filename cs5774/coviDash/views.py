from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.urls import resolve
from django.http import JsonResponse
from .models import Rumour, Vote, Comment, Updoots, Source
from actions.models import Action
from django.contrib.auth.models import User
from django.core import serializers
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime

def home(request):
    #pass detailed user data if logged in for dashboard otherwise empty userData will be passed
    if request.session.get('userid', None) != None:
        tempUser = User.objects.get(pk=request.session.get('userid', None))

        #Rumours tied to the user
        involvedRumours = tempUser.details.subscribed.all().values_list('pk') | Rumour.objects.filter(poster=tempUser).values_list('pk')

        #Votes relating to user based on rumours
        involvedVotes = Vote.objects.filter(rumour_id__in=involvedRumours)

        #Comments related based on rumours
        involvedComments = Comment.objects.filter(rumour_id__in=involvedRumours)

        #Query actions for all actions relating to user
        actions = Action.objects.filter(user=tempUser) | Action.objects.filter(target_ct=ContentType.objects.get_for_model(Rumour).id, target_id__in=involvedRumours) | Action.objects.filter(target_ct=ContentType.objects.get_for_model(Vote).id, target_id__in=involvedVotes) | Action.objects.filter(target_ct=ContentType.objects.get_for_model(Comment).id, target_id__in=involvedComments)
        
        #Add promotions and demotions if admin or dev
        if request.session.get('role') != 'regular':
            actions = actions | Action.objects.filter(verb__in=['UP','DP'])

        #Filter out dupes, newest first
        actions = actions.distinct().order_by('-date')[:20]

        #Temporary dashboard list
        added = Rumour.objects.filter().values_list('pk').order_by('-date')[:4]

        #Get numbers 
        numPoster = tempUser.details.get_posted()
        numCited = tempUser.details.get_cited()
        numSolved = tempUser.details.get_solved()

        userData = {
            #mess around with added later
            'posted': numPoster,
            'cited': numCited,
            'solved': numSolved,
            'title': tempUser.details.get_title()
        }

        return render(request, 'coviDash/home.html', {
            'dash': Rumour.objects.filter(pk__in=added).order_by('-date'),
            'rumours': Rumour.objects.exclude(pk__in=added).order_by('-date'),
            'userData': userData,
            'actions': actions
        })
    else: 
        return render(request, 'coviDash/home.html',{
            'rumours': Rumour.objects.all().order_by('-date')
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
            poster__username__icontains=query
        ).order_by(sortQ)

    if(resolve(request.path_info).url_name == 'admin'): 
        return render(request, 'coviDash/list.html', {
            'rumours': resultRumours,
            'users': User.objects.all()
        })

    return render(request, 'coviDash/list.html', {
        'rumours': resultRumours
    })

def detail(request, rumour_id):
    #Check for id in list
    rumour = Rumour.objects.get(pk=rumour_id)
    comments = Comment.objects.filter(rumour_id = rumour_id).order_by('-date')

    return render(request, 'coviDash/detail.html', {
        'rumour': rumour,
        'comments': comments
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

        tempuser = User.objects.get(pk=request.session.get('userid'))

        newRumour = Rumour(
            title = addTitle,
            description = addDesc,
            bodyHtml = addBody,
            img = addImg,
            poster = tempuser
        )

        newRumour.save()

        activityLog = Action(
            user = tempuser,
            verb = "AR",
            target = newRumour,
        )

        activityLog.save()

        #Subscribe user to the rumour
        tempuser.details.subscribed.add(newRumour)
        tempuser.save()

        tempuser.details.check_level()

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
        tempuser = User.objects.get(pk=request.session.get('userid'))

        #pull post variables
        editTitle = request.POST.get("title")
        editDesc = request.POST.get("description")
        editBody = request.POST.get("bodytext")
        editImg = request.POST.get("picture")

        rumour.title = editTitle
        rumour.description = editDesc
        rumour.bodyHtml = editBody
        rumour.img = editImg
        rumour.edited = datetime.now()

        rumour.save()

        #message for testing. replace with db code in next project
        messages.add_message(request, messages.INFO, "You have successfully edited the rumour: " + editTitle)

        activityLog = Action(
            user = tempuser,
            verb = "RE",
            target = rumour,
        )

        activityLog.save()

        #Subscribe user to the rumour if not already subscribed
        if rumour not in tempuser.details.subscribed.all():
            tempuser.details.subscribed.add(rumour)
            tempuser.save()

        tempuser.details.check_level()

        #back whence you came
        return redirect('coviDash:rumour-detail', rumour_id=rumour_id)
    

    #Show form
    return render(request, 'coviDash/add.html', {
        'rumour': rumour
    })

def delete(request):
    #get posted stuff
    removeId = request.POST.get("rumourId")

    commentIds = Comment.objects.filter(rumour_id = removeId).values_list('pk')
    voteIds = Vote.objects.filter(rumour_id = removeId).values_list('pk')

    #Clear actions, comments and votes with this rumour
    Action.objects.filter(target_ct=ContentType.objects.get_for_model(Rumour).id, target_id=removeId).delete()
    Action.objects.filter(target_ct=ContentType.objects.get_for_model(Comment).id, target_id__in=commentIds).delete()
    Action.objects.filter(target_ct=ContentType.objects.get_for_model(Vote).id, target_id__in=voteIds).delete()

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
        tempuser = User.objects.get(pk=request.session.get('userid'))

        try:
            rumour = Rumour.objects.get(pk=rumourId)
            val = 0

            if validity == "true": 
                #True
                val = 1

            elif validity == "false": 
                #False
                val = -1
                    
            vote = Vote (
                voter = tempuser,
                rumour = rumour,
                validity = val,
            )

            vote.save()

            #Update validity tag
            voteList = Vote.objects.filter(rumour = rumour)

            trueVotes = voteList.filter(validity = 1).count()

            falseVotes = voteList.filter(validity = -1).count()

            totalVotes = trueVotes + falseVotes

            fpercent = falseVotes/totalVotes

            if totalVotes > 10: 
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

            activityLog = Action(
                user = tempuser,
                verb = "RV",
                target = vote,
            )

            activityLog.save()

            #Subscribe user to the rumour if not already subscribed
            if rumour not in tempuser.details.subscribed.all():
                tempuser.details.subscribed.add(rumour)
                tempuser.save()

            tempuser.details.check_level()

            return JsonResponse({
                'success': 'success', 
                'true': rumour.get_votes().get('true'),
                'false': rumour.get_votes().get('false'),
                'validity': rumour.validity
            }, status=200)

        except Rumour.DoesNotExist:
            return JsonResponse({'error': 'No rumour found'}, status=200)

    else: 
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
def addcomment(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax and request.method == "POST":
        temprumour = Rumour.objects.get(pk=request.POST.get("rumourid"))
        tempbody = request.POST.get("commentbody")
        tempuser = User.objects.get(pk=request.session.get('userid'))

        newComment = Comment(
            commenter = tempuser,
            body = tempbody,
            rumour = temprumour
        )

        newComment.save()

        activityLog = Action(
            user = tempuser,
            verb = "RC",
            target = newComment,
        )

        activityLog.save()
        
        #Subscribe user to the rumour if not already subscribed
        if temprumour not in tempuser.details.subscribed.all():
            tempuser.details.subscribed.add(temprumour)
            tempuser.save()
        
        tempuser.details.check_level()

        return JsonResponse({
            'success': 'success', 
            'commenterUrl': tempuser.details.get_absolute_url(),
            'commenter': tempuser.details.get_name(),
            'commenterTitle': tempuser.details.get_title(),
            'id': newComment.pk,
            'body': newComment.body,
            'time': naturaltime(newComment.date)
        }, status=200)
        
    else: 
        return JsonResponse({'error': 'Invalid request'}, status=400)

def editcomment(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax and request.method == "POST":
        commentid = request.POST.get('id')
        commentbody = request.POST.get('body')
        editdate = datetime.now()

        comment = Comment.objects.get(pk = commentid)
        comment.body = commentbody
        comment.edited = editdate

        comment.save()

        #Subscribe user to the rumour if not already subscribed
        if comment.rumour not in comment.commenter.details.subscribed.all():
            comment.commenter.details.subscribed.add(comment.rumour)
            comment.commenter.save()

        return JsonResponse({
            'success': 'success', 
            'id': comment.pk,
            'body': comment.body,
            'time': naturaltime(editdate)
        }, status=200)
    else: 
        return JsonResponse({'error': 'Invalid request'}, status=400)

def removecomment(request):
    #Pretty much the same as removing anything else
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax and request.method == "POST":
        commentId = request.POST.get('id');

        comment = Comment.objects.get(pk=commentId);

        #Find actions with this comment and delete
        Action.objects.filter(target_ct=ContentType.objects.get_for_model(Comment).id, target_id=commentId).delete()

        comment.delete();

        return JsonResponse({
            'success': 'success', 
            'id': commentId,
        }, status=200)
        
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