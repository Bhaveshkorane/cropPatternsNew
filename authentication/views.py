
from django.shortcuts import render,redirect

# For user creation and login
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views.decorators.cache import cache_control
from django.contrib import messages

# For message logging 
import logging
logger = logging.getLogger('django')


def registeruser(request):
    context = {'uname': "", 'email': "", 'pass1': "", 'pass2': "", 'fname': "", 'lname': ""}

    if request.method == "POST":
        uname = request.POST.get('uname')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('uemail')
        pass1 = request.POST.get('Password1')
        pass2 = request.POST.get('Password2')

        if pass1 == pass2:
            if not User.objects.filter(username=uname).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=uname, email=email, password=pass1, first_name=fname, last_name=lname)
                    user.save()
                    messages.success(request, "User created successfully")
                    logger.info(f"user {uname} has been registered successfully")
                    return redirect('/login/')
                else:
                    messages.error(request, "Email Already Exists")
            else:
                messages.error(request, "Username already exists")
        else:
            messages.error(request, "Passwords do not match")
        context = {'uname': uname, 'email': email, 'pass1': pass1, 'pass2': pass2, 'fname': fname, 'lname': lname}
    return render(request, 'registration.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginuser(request):
    if request.user.is_authenticated:
        return redirect("/home/")
    if request.method == "POST":
        uname = request.POST.get('uname')
        password = request.POST.get('Password')

        user = authenticate(request,username=uname, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"user {uname} has been logged in ")
            return redirect('/home/')
        else:
            messages.error(request, "Please Enter the correct Credentials")
               
    return render(request, 'login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logouturl(request):
    logout(request)
    logger.info(f"user has been logged out ")
    return redirect('/login/')