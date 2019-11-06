from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'products/home.html')

def create(request):
    pass