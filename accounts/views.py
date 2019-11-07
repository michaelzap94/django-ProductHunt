from django.shortcuts import render, redirect

#================================================================
#IMPORT THE DJANGO BUILT-IN ADMIN Model 'User'
from django.contrib.auth.models import User
#IMPORT THE DJANGO BUILT-IN ADMIN authentication SYSTEM
from django.contrib import auth
#================================================================

#'user' is a special keyword, that can be accessed from inside the templates.
# in html templates using 'user'|'user.is_authenticated' or django .py files using 'request.user'|'request.user.is_authenticated'.

# Create your views here.
def signup(request):
    if (request.method == 'POST'):
        if request.POST['password1'] == request.POST['password2']:
            try:
                #get a record, by using the 'username'
                User.objects.get(username=request.POST['username'])
                return render(request, 'accounts/signup.html', {'error':'Username has been taken.'})
            except User.DoesNotExist:
                # CREATES a user object in the User Model, so the user can login.
                user = User.objects.create_user(username = request.POST['username'], password = request.POST['password1'])
            # WILL LOG THE USER IN, and will save the instance in the STATE cookie 'sessionid',
                # therefore, you can use user.is_authenticated to check if the user is logged in.
                # 'user' will be available Globally after doing auth.login(request, user), in html templates using 'user'|'user.is_authenticated' or django .py files using 'request.user'|'request.user.is_authenticated'.
                auth.login(request, user)
                return redirect('home')
    else:
        return render(request, 'accounts/signup.html')

def login(request):
    if(request.method == 'POST'):
        # try to authenticate, if success, return a user object.
        user = auth.authenticate(username = request.POST['username'], password = request.POST['password'])
        # authentication successful
        if user is not None:
            # WILL LOG THE USER IN, and will save the instance in the STATE cookie 'sessionid',
            # therefore, you can use user.is_authenticated to check if the user is logged in.
            # 'user' will be available Globally after doing auth.login(request, user), in html templates using 'user'|'user.is_authenticated' or django .py files using 'request.user'|'request.user.is_authenticated'.
            auth.login(request, user)
            return redirect('home')
        # authentication failed
        else:
            return render(request, 'accounts/signup.html', {'error':'Username or password is incorrect.'})
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    if(request.method == 'POST'):
        #destroys the user object stored in the cookie 'sessionid'.
        auth.logout(request)
        return redirect('home')