from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, redirect


def dashboard(request, pk):
    if request.method == 'GET':
        return render(request, 'dashboard.html')


def issues(request, pk):
    if request.method == 'GET':
        return render(request, 'issues.html')


def statistics(request, pk):
    if request.method == 'GET':
        return render(request, 'statistics.html')


def settings(request, pk):
    if request.method == 'GET':
        return render(request, 'settings.html')
