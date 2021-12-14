import datetime
import time
import collections
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
        top_ten = models.Issues.objects.filter(project_id=pk, assign__isnull=False).order_by('-create_time')[:5]
        return render(request, 'dashboard.html', {'status_dic': status_dic, 'users': users, 'top_ten': top_ten})


def chart(request, pk):
    res = ApiResponse()
    # 取30天的
    time_now = datetime.datetime.now().date()
    query_set = models.Issues.objects.filter(project_id=pk, create_time__gte=time_now - datetime.timedelta(days=30)). \
        extra(select={'ctime': 'Date_Format(web_issues.create_time,"%%Y-%%m-%%d")'}).values('ctime').annotate(
        ct=Count('id'))
    # <QuerySet [{'ctime': '2021-12-04', 'ct': 23}]>

    date_dic = collections.OrderedDict()
    for i in range(30):
        date = time_now - datetime.timedelta(days=i)
        date_dic[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple())*1000, 0] # 单位是毫秒
    for query in query_set:
        date_dic[query['ctime']][-1] += query.get('ct', 0)

    res.series = list(date_dic.values())
    return JsonResponse(res.data)


def statistics(request, pk):
    if request.method == 'GET':
        return render(request, 'statistics.html')
