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
# built-in @user_passes_test(your_function) will make "your_function" to take as argument 'request.user' only.
# Therefore, if you need to use more arguments. e.g: product_id, create your own decorator, as I did with '@delete_product_authorization'

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

# OWN function, that will be used as a middleware decorator: 
# WILL check if the user making the request to delete the product was the user that created the product
def delete_product_authorization(delete):
    def inner(request,product_id):
        try:
            productToDelete = Product.objects.get(id=product_id)
            creatorId = productToDelete.hunter.id
            if(creatorId == request.user.id):
                return delete(request,product_id)
            else:
                raise Exception('You are not authorized to delete this product.')
        except Exception as anyException:
            print(anyException)
            return redirect('home')
    return inner


#FIRST CHECK THE USER IS LOGGEDIN, THEN CHECK IF USER IS AUTHORIZED TO PERFORM THIS ACTION
@login_required(login_url='/accounts/signup')
@delete_product_authorization
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





