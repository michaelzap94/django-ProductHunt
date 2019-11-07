from django.shortcuts import render, redirect
from django.utils import timezone

#import the Product Model
from .models import Product

#IMPORT THE DJANGO BUILT-IN login_required (MIDDLEWARE) "decorator" TO MAKE SURE login is required to access something.
from django.contrib.auth.decorators import login_required
# this decorator will redirect the user to the login page (BY DEFAULT) if the user is not logged in.
# YOU CAN ALSO pass a parameter login_url in it: @login_required(login_url='/accounts/signup')

# user_passes_test(funtion, login_url = 'home') will accept a function that returns True or False, to check if user passes the test
# if True continue, otherwise, specify login_url to redirect the user.
# built-in @user_passes_test requires:
from functools import wraps
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url



def home(request):
    #get all objects in Products
    allProductObjects = Product.objects
    return render(request, 'products/home.html',{'products':allProductObjects})

@login_required
def create(request):
    if(request.method == 'POST'):
        if request.POST['title'] and request.POST['body'] and request.POST['url'] and request.FILES['image'] and request.FILES['icon']:
            objProduct = Product()
            objProduct.title = request.POST['title']
            objProduct.body = request.POST['body']
            #check if url is valid
            if request.POST['url'].startswith('http://') or request.POST['url'].startswith('https://'):
                objProduct.url = request.POST['url']
            else:
                objProduct.url = 'http://' + request.POST['url']

            objProduct.image = request.FILES['image']
            objProduct.icon = request.FILES['icon'] # request.POST['icon'] not valid, as request.POST will not contain 'files' type.
            objProduct.pub_date = timezone.datetime.now()
            objProduct.hunter = request.user # whoever the user CREATED this request
            #THIS WILL SAVE THE OBJECT
            objProduct.save()
            return redirect('home')
            
        else:
            return render(request, 'products/create.html', {'error':'All fields are required'})
    else:
        return render(request, 'products/create.html')

def detail(request, product_id):
    # get an object using its id ALTERNATIVE TO:     product = get_object_or_404(Product, pk=id)
    try:
        productDetail = Product.objects.get(pk=product_id)
    except Exception as anyException:
        return render(request,'products/home.html', {'error':anyException})
    #else will only run if try was successful
    else:
        return render(request,'products/detail.html', {'product':productDetail})

@login_required(login_url='/accounts/signup')
def upvote(request, product_id):
    # IF YOU WANT TO UPDATE 
    # 1ST ALTERNATIVE: MyModel.objects.filter(pk=some_value).update(field1='some value'), OTHERWISE:
    # 1) get the object you want to update
    try:
        productObj = Product.objects.get(pk=product_id)
        productObj.makeUpvote() # I modified it so it adds 1 to the total_votes
        productObj.save()     

    except Exception as anyException:
        return render(request,'products/home.html', {'error':anyException})
    else:
        #return redirect('/products/'+str(productObj.id)) # I could have also used product_id parameter
        return redirect(request.META['HTTP_REFERER']) # like redirect('back') in node.js


#===============================================================
def custom_user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

#===============================================================

def authorization_required(user, product_id):
    try:
        productToDelete = Product.objects.get(id=product_id)
        creatorId = productToDelete.hunter.id
        if(creatorId == user.id):
            return True
        else:
            raise Exception('You are not authorized to delete this product.')
    except Exception as anyException:
        print(anyException)
        return False
#===============================================================

#FIRST CHECK THE USER IS LOGGEDIN, THEN CHECK IF USER IS AUTHORIZED TO PERFORM THIS ACTION
@login_required(login_url='/accounts/signup')
@custom_user_passes_test(authorization_required)
def delete(request, product_id):
    #IF YOU WANT TO DELETE:
    # 1ST ALTERNATIVE: SomeModel.objects.filter(id=id).delete(), otherwise
    # delete it from an instance:
    try:
        productToDelete = Product.objects.get(id=product_id)
        creatorId = productToDelete.hunter.id
        if(creatorId == request.user.id):
            productToDelete.delete()
        else:
            raise Exception('You are not authorized to delete this product.')
    except Exception as anyException:
        return render(request,'products/home.html', {'error':anyException})
    else:
        return redirect('home')

# x = custom_user_passes_test(authorization_required)(delete)





