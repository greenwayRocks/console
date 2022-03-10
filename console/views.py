from django.shortcuts import render

# Create your views here.

def index(request):
    # context = { "text": "Hello, from views!"}
    context = {}
    return render(request, 'base.html', context)
