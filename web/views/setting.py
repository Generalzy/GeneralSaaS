from django.shortcuts import render, redirect
from utils.response import ApiResponse
from django.http import JsonResponse
from web import models
from libs.tencent.cos import delete_bucket
from web.forms import UpdateUserPasswordForm
from utils.secret import get_secret
from threading import Thread


def settings(request):
    if request.method == 'GET':
        user = request.authentication
        project = models.Project.objects.filter(creator=user)
        return render(request, 'settings.html', locals(), status=200)


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
            # 此处改为异步
            t = Thread(target=delete_bucket, args=(project.bucket,))
            # delete_bucket(bucket=project.bucket)
            t.start()
            project.delete()
            return redirect('project_list')


def password(request):
    if request.method == 'GET':
        return render(request, 'settingspassword.html', locals(), status=200)
    if request.method == "POST":
        response = ApiResponse()
        form = UpdateUserPasswordForm(data=request.POST)

        if form.is_valid():
            old_password, new_password = form.cleaned_data['password'], form.cleaned_data["new_password"]
            user = request.authentication  # type:models.UserInfo
            if user.password == get_secret(old_password):
                new_password_secret = get_secret(new_password)
                if user.password == new_password_secret:
                    response.code = 0
                    response.error = "新密码和旧密码重复"
                else:
                    user.password = new_password_secret
                    user.save()
                    response.url = "/login"
                    request.session.flush()
            else:
                response.code = 0
                response.error = "旧密码错误"
        else:
            response.error = form.errors.as_text()
            response.code = 0

        return JsonResponse(data=response.data)


def issue(request):
    if request.method == "GET":
        projects = models.Project.objects.filter(creator=request.authentication).all()
        return render(request, "settingsissue.html", locals(), status=200)

    if request.method == "POST":
        response = ApiResponse()
        title = request.POST.get("title", "")
        project = request.POST.get("project", "")

        if title and project:
            issue_obj = models.IssuesType.objects.create(project_id=project, title=title)
            response.title = issue_obj.title
        else:
            response.code = 0
            response.error = "项目名或issue为空"

        return JsonResponse(data=response.data)


def model(request):
    if request.method == "GET":
        projects = models.Project.objects.filter(creator=request.authentication).all()
        return render(request, "settingsmodel.html", locals(), status=200)

    if request.method == "POST":
        response = ApiResponse()
        title = request.POST.get("title", "")
        project = request.POST.get("project", "")

        if title and project:
            issue_obj = models.Module.objects.create(project_id=project, title=title)
            response.title = issue_obj.title
        else:
            response.code = 0
            response.error = "项目名或model为空"

        return JsonResponse(data=response.data)
