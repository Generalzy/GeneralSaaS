from django.shortcuts import render, redirect
from django.http import JsonResponse
from utils.response import ApiResponse
from web import models
from libs.tencent.cos import delete_bucket


def settings(request):
    if request.method == 'GET':
        return render(request, 'settings.html')


def delete(request):
    if request.method == 'GET':
        return render(request, 'settingsdelete.html')
    elif request.method == 'POST':
        res = ApiResponse()
        project_name = request.POST.get('pname')
        project = models.Project.objects.filter(creator=request.authentication, name=project_name).first()
        if not project:
            res.code = 0
            res.msg = '请填写正确的项目名'
            return render(request, 'settingsdelete.html', res.data)
        else:
            # 删除
            # 必须删除所有文件和碎片
            delete_bucket(bucket=project.bucket)
            project.delete()
            return redirect('project_list')


def password(request):
    if request.method == 'GET':
        return render(request, 'settingspassword.html')
