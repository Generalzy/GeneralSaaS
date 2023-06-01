import datetime
import time
import collections
from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, redirect
from web import models
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt


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
        # 获取当前项目
        project_own = request.project.creator.pk
        if project_own != request.authentication.pk:
            # 如果当前用户是参与者
            users.append(request.project.creator.username)
        # users需要去重
        users = list(set(users))
        top_ten = models.Issues.objects.filter(project_id=pk, assign__isnull=False).order_by('-create_time')[:5]

        # 任务提醒
        issue_count = models.Issues.objects.filter(project_id=pk, assign=request.authentication, status__in=(
            1, 2, 5, 7
        )).count()

        return render(request, 'dashboard.html', {
            'status_dic': status_dic, 'users': users, 'top_ten': top_ten, "issue_count": issue_count,
        })


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
        date_dic[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple()) * 1000, 0]  # 单位是毫秒
    for query in query_set:
        date_dic[query['ctime']][-1] += query.get('ct', 0)

    res.series = list(date_dic.values())
    return JsonResponse(res.data)


@csrf_exempt
def statistics(request, pk):
    if request.method == 'GET':
        return render(request, 'statistics.html')
    elif request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')

        # 查询issue
        # 1. 将priority映射为name
        # 2. 按照id分组聚合求count
        # 3. 导入name和y
        b_data = models.Issues.objects.filter(project_id=pk, create_time__gte=start, create_time__lte=end).extra(
            select={'name': 'priority'}
        ).values('name').annotate(y=Count('id'))

        res = ApiResponse()
        res.BinData = list(b_data)

        users = [request.project.creator]
        for item in models.ProjectUser.objects.filter(project_id=pk).all():
            users.append(item.user)

        temp = []
        for user in users:
            dic = dict().fromkeys(list(range(1, 8)), 0)
            obj = models.Issues.objects.filter(project_id=pk, assign=user, create_time__gte=start,
                                               create_time__lte=end).values('status').annotate(
                data=Count('id'))

            for item in obj:
                dic[item['status']] += item['data']
            temp.append({
                'name': user.username,
                'data': list(dic.values())
            })

        res.categories = [
            '新建',
            '处理中',
            '已解决',
            '已忽略',
            '待反馈',
            '已关闭',
            '重新打开',
        ]
        res.series = temp
        return JsonResponse(res.data)
