from django.shortcuts import render,redirect

from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.http import HttpResponse

from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.forms import UserCreationForm

from .models import Room,Topic,Message

from django.contrib.auth.models import User 

from .forms import RoomForm,UserForm

from django.contrib import messages



# Create your views here.


# rooms=[

#     {'id':1,'name':'Lets learn python!'},

#     {'id':2,'name':'dive into infinite knowledge'},

#     {'id':3,'name':'Frontend devlopers'},


# ]



def loginpage(request):
    page='login'

    if request.user.is_authenticated:

        return redirect('home')
    

    if request.method =="POST":

        username = request.POST.get('username')

        password=request.POST.get('password')

        try:

            user=User.objects.get(username=username)

        except:

            messages.error(request,'User does not exist')

        user= authenticate(request, username=username, password=password)


        if user is not None:

            print("login successfull")
            login(request,user)

            return redirect('home')

        else:

            messages.error(request,'Username or password doesnot exist')

    context={'page':page}

    return render(request,'login_register.html',context)


def logountUser(request):
    logout(request)

    return redirect('home')


def registerpage(request):

    form=UserCreationForm()
    

    if request.method=='POST':

        form=UserCreationForm(request.POST)

        if form.is_valid():
            print("form is valid")
            user=form.save(commit=False)

            user.username=user.username.lower()

            user.save()
            login(request,user)

            return redirect('home')

        else:
            
            messages.error(request,"An Error occured during registration")
            
    

    return render(request,'login_register.html',{'form':form})


def home(request):

    q=request.GET.get('q') if request.GET.get('q')!=None else ""

    rooms=Room.objects.filter(

        Q(topic__name__icontains=q) |

        Q(name__icontains=q) |

        Q(description__icontains=q)   
        )

    room_count=rooms.count() 

    topics=Topic.objects.all()[0:5]
    

    room_messages=Message.objects.filter(Q(room__name__icontains=q))
    

    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}

    return render(request,'home.html',context)


def room(request,pk):

    rooms=Room.objects.get(id=pk)

    room_messages=rooms.message_set.all()
    participants=rooms.participants.all()

    if request.method=='POST':

        print('receive message')

        message=Message.objects.create(
            user=request.user,
            room=rooms,

            body=request.POST.get('body')
        )
        rooms.participants.add(request.user)

        return redirect('room', pk=rooms.id)

    context={'room':rooms,'room_messages':room_messages,'participants':participants}            

    return render(request,'room.html',context)


def userProfile(request,pk):

    user=User.objects.get(id=pk)

    rooms=user.room_set.all()

    room_message=user.message_set.all()

    topics=Topic.objects.all()

    context={'user':user,'rooms':rooms,'room_message':room_message,'topics':topics}

    return render(request,'profile.html',context)


@login_required(login_url='login')

def createRoom(request):

    form=RoomForm()

    topics=Topic.objects.all()

    if request.method == 'POST':

        topic_name = request.POST.get('topic')

        topic, created = Topic.objects.get_or_create(name=topic_name)


        Room.objects.create(

            host=request.user,
            topic=topic,

            name=request.POST.get('name'),

            description=request.POST.get('description'),
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}

    return render(request, 'room_form.html', context)
    

@login_required(login_url='login')

def updateRoom(request,pk):

    room=Room.objects.get(id=pk)

    form=RoomForm(instance=room)

    topics=Topic.objects.all()

    if request.user != room.host:

        return HttpResponse("Your are not allowed here!!")
    

    if request.method=='POST':

        form=RoomForm(request.POST,instance=room)

        topic,created=Topic.objects.get_or_create(name=topic_name)

        room.name=request.POST.get('name')
        room.topic=topic

        room.description=request.POST.get('description')


        # if form.is_valid():

        #     form.save()

        return redirect('home')

    context={'form':form}

    return render(request,'room_form.html',context)


@login_required(login_url='login')

def deleteRoom(request,pk):

    room=Room.objects.get(id=pk)

    if request.user != room.host:

        return HttpResponse("Your are not allowed here!!")

    if request.method =='POST':
        room.delete()

        return redirect('home')
    

    return render(request,'delete.html', {'obj':room})


@login_required(login_url='login')

def deleteMessage(request,pk):

    message=Message.objects.get(id=pk)

    if request.user != message.user:

        return HttpResponse("Your are not allowed here!!")

    if request.method =='POST':
        message.delete()

        return redirect('home')
    

    return render(request,'delete.html', {'obj':message})

def jls_extract_def():
    
    return 


@login_required(login_url='login')

def updateuser(request):
    user=request.user
    form=UserForm(instance=user)
    
    if request.method=='POST':
        form=UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            redirect('user-profile',pk=user.id)
    return render(request,'update-user.html',{'form':form})
    
    
def topicsPage(request):
    
    q = request.GET.get('q') if request.GET.get('q')!=None else ""
    topics=Topic.objects.filter(name__icontains = q)
    return render(request,'topics.html',{'topics':topics})


def activityPage(request):
    room_messages=Message.objects.all()
    return render(request,'activity.html',{'room_messages':room_messages})