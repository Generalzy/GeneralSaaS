import time
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web.forms import ProjectForm
from utils.response import ApiResponse
from django.db import transaction
from web import models
from libs.tencent.cos import create_bucket, region


def project_list(request):
    # print(request.authentication) UserInfo object(6)
    # print(request.price)          PricePolicy object(1)
    if request.method == 'GET':
        projects_dic = {
            'star': [],
            'mine': [],
            'join': []
        }
        my_projects = models.Project.objects.filter(creator=request.authentication)
        for project in my_projects:
            if project.star:
                projects_dic['star'].append({'obj': project, 'ptype': 'mine'})
            else:
                projects_dic['mine'].append({'obj': project, 'ptype': 'mine'})
        join_projects = models.ProjectUser.objects.filter(user=request.authentication)
        for project_user in join_projects:
            if project_user.stat:
                projects_dic['star'].append({'obj': project_user.project, 'ptype': 'join'})
            else:
                projects_dic['join'].append({'obj': project_user.project, 'ptype': 'join'})
        form = ProjectForm()
        return render(request, 'project_list.html', {'form': form, 'project_dic': projects_dic})
    elif request.method == 'POST':
        res = ApiResponse()
        form = ProjectForm(request=request, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 提前将创建者放进去
                user = request.authentication
                bucket = f'{user.phone}-{str(int(time.time()))}-1306501644'
                create_bucket(bucket)
                form.instance.creator = user
                form.instance.region = region
                form.instance.bucket = bucket
                # save只保存form组件中的值
                form.save()
                user.project_num += 1
                user.save()
                return JsonResponse(res.data)
        else:
            res.code = 0
            res.msg = '创建失败'
            res.errors = form.errors
            return JsonResponse(res.data)


def project_star(request, ptype, pk):
    if ptype == 'mine':
        models.Project.objects.filter(pk=pk, creator=request.authentication).update(star=True)
        return redirect('project_list')
    elif ptype == 'join':
        models.ProjectUser.objects.filter(user=request.authentication, project__id=pk).update(stat=True)
        return redirect('project_list')
    return HttpResponse('非法操作')


def project_unstar(request, ptype, pk):
    if ptype == 'mine':
        models.Project.objects.filter(pk=pk, creator=request.authentication).update(star=False)
        return redirect('project_list')
    elif ptype == 'join':
        models.ProjectUser.objects.filter(user=request.authentication, project__id=pk).update(stat=False)
        return redirect('project_list')
    return HttpResponse('非法操作')
