from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, redirect
from web import models
from django.db.models import Count


def dashboard(request, pk):
    if request.method == 'GET':
        issues_data = models.Issues.objects.filter(project=request.project).values('status').annotate(ct=Count('id'))
        status_dic = {}
        for key, val in models.Issues.status_choice:
            status_dic[key] = {'text': val, 'count': 0}
        for item in issues_data:
            status_dic[item['status']]['count'] += item['ct']

        users = [request.authentication.username]
        for pu_obj in models.ProjectUser.objects.filter(project_id=pk).all():
            users.append(pu_obj.user.username)
        return render(request, 'dashboard.html', {'status_dic': status_dic, 'users': users})


def issues(request, pk):
    if request.method == 'GET':
        return render(request, 'issues.html')


def statistics(request, pk):
    if request.method == 'GET':
        return render(request, 'statistics.html')
