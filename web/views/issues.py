import json
import uuid
from django.core.cache import cache
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from utils.page import Pagination
from web.forms import IssuesModelForm, InviteModelForm
from web import models
from utils.response import ApiResponse
from django.views.decorators.csrf import csrf_exempt
from utils.checkfilter import CheckFilter


def issues(request, pk):
    res = ApiResponse()
    if request.method == 'GET':
        trans_obj = models.Transaction.objects.filter(user=request.authentication).first()
        number = trans_obj.price_policy.project_member - request.project.join_count
        invite_form = InviteModelForm()
        status = request.GET.get('status', None)
        current_page = request.GET.get('page')
        check_filter = CheckFilter(models.Issues.status_choice, request)
        if status:
            temp = models.Issues.objects.filter(project=request.project, status=status).all()
        else:
            temp = models.Issues.objects.filter(project=request.project).all()
        all_count = temp.count()
        form = IssuesModelForm(request=request)
        page_obj = Pagination(current_page=current_page, all_count=all_count, status=status)
        data = temp[page_obj.start:page_obj.end]
        return render(request, 'issues.html',
                      {'page_obj': page_obj, 'form': form, 'data': data, 'check_filter': check_filter,
                       'invite_form': invite_form, 'number': number})
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


def code(request, pk):
    if request.method == 'POST':
        res = ApiResponse()
        form = InviteModelForm(data=request.POST)
        trans_obj = models.Transaction.objects.filter(user=request.authentication).first()
        number = trans_obj.price_policy.project_member
        join_count = request.project.join_count
        if form.is_valid():
            if request.authentication != request.project.creator:
                res.code = '只有项目创建者才可以邀请成员!'
            elif join_count >= number:
                res.code = '本项目人员已经达到限额，无法生成邀请码！'
            else:
                geb_code = f'{uuid.uuid4()}'
                res.code = f'{request.scheme}://{request.get_host()}{reverse("inviteIssue")}/?code={geb_code}&pk={pk}'
                form.instance.creator = request.authentication
                form.instance.project = request.project
                form.instance.code = geb_code
                form.save()
                period = form.cleaned_data.get('period')
                if period:
                    cache.set(f'{pk}_invite_code_', geb_code, period * 60)
                else:
                    cache.set(f'{pk}_invite_code_', geb_code)
        else:
            res.code = '异常错误！'
        return JsonResponse(res.data)


def invite(request):
    if request.method == 'GET':
        pk = request.GET.get('pk')
        geb_code = request.GET.get('code')

        project_obj = models.Project.objects.filter(pk=pk).first()
        trans_obj = models.Transaction.objects.filter(user=request.authentication).first()
        number = trans_obj.price_policy.project_member
        join_count = project_obj.join_count

        ture_code = cache.get(f'{pk}_invite_code_', None)
        invite_obj = models.ProjectInvite.objects.filter(project_id=pk).first()

        if geb_code == ture_code and invite_obj.creator != request.authentication:
            msg = '成功加入此项目'
            models.ProjectUser.objects.create(project_id=pk, user=request.authentication)
            project_obj.join_count += 1
            project_obj.save()
        elif join_count >= number:
            msg = '加入失败，项目人员已满'
        else:
            msg = '未知错误'
        return render(request, 'issueInvite.html', {'msg': msg})
