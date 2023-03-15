from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def helper(request):
    return render(request, "helper.html")
