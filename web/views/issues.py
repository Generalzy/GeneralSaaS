import json
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.page import Pagination
from web.forms import IssuesModelForm
from web import models
from utils.response import ApiResponse
from django.views.decorators.csrf import csrf_exempt
from utils.checkfilter import CheckFilter


def issues(request, pk):
    res = ApiResponse()
    if request.method == 'GET':
        status = request.GET.get('status', None)
        current_page = request.GET.get('page')
        print(status)
        check_filter = CheckFilter(models.Issues.status_choice, request)
        if status:
            temp = models.Issues.objects.filter(project=request.project, status=status).all()
        else:
            temp = models.Issues.objects.filter(project=request.project).all()
        all_count = temp.count()
        form = IssuesModelForm(request=request)
        page_obj = Pagination(current_page=current_page, all_count=all_count,status=status)
        data = temp[page_obj.start:page_obj.end]
        return render(request, 'issues.html',
                      {'page_obj': page_obj, 'form': form, 'data': data, 'check_filter': check_filter})
    elif request.method == 'POST':
        form = IssuesModelForm(data=request.POST, request=request)
        if form.is_valid():
            form.instance.project = request.project
            form.instance.creator = request.authentication
            form.save()
            return JsonResponse(res.data)
        else:
            res.code = 0
            res.msg = form.errors
            return JsonResponse(res.data)


@csrf_exempt
def edit_issue(request, pk, issue_id):
    if request.method == 'GET':
        issue = models.Issues.objects.filter(pk=issue_id).first()
        form = IssuesModelForm(request=request, instance=issue)
        return render(request, 'issueEdit.html', {'form': form, 'issue': issue, 'issue_id': issue_id})
    elif request.method == 'POST':
        res = ApiResponse()
        data = json.loads(request.body)
        filed = data.get('field')
        value = data.get('value')
        issue_obj = models.Issues.objects.filter(project_id=pk, pk=issue_id).first()
        setattr(issue_obj, filed, value)
        issue_obj.save()
        return JsonResponse(res.data)


@csrf_exempt
def record_issue(request, pk, issue_id):
    if request.method == 'GET':
        rows = models.IssuesReply.objects.filter(issues_id=issue_id, issues__project=request.project).order_by(
            '-reply_type')
        # 转为json格式
        data_list = []
        for row in rows:
            data_list.append({
                'id': row.id,
                'name': row.creator.username[0],
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_time': row.creat_time.strftime('%Y-%m-%d %H:%M'),
                'parent': None or row.reply_id
            })
        return JsonResponse({'data': data_list})
    elif request.method == 'POST':
        res = ApiResponse()
        parent = request.POST.get('parent', None)
        content = request.POST.get('val')
        models.IssuesReply.objects.create(reply_type=2, reply_id=parent, content=content,
                                          creator=request.authentication, issues_id=issue_id)
        return JsonResponse(res.data)
