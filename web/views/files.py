from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, redirect
from web.forms import FileModelForm
from django.urls import reverse
from web import models
from django.views.decorators.csrf import csrf_exempt
from libs.tencent.cos import upload_file
from utils.secret import get_key


# url: http://127.0.0.1:8000/manage/file/1/?folder=9
def file(request, pk):
    res = ApiResponse()
    folder = request.GET.get('folder', None)  # type:str
    if folder and folder.isdigit():
        parent = models.File.objects.filter(pk=folder, project=request.project, file_type=2).first()
    else:
        parent = None

    if request.method == 'GET':
        current = parent
        paths = []
        while current:
            paths.insert(0, {'id': current.id, 'name': current.name})
            current = current.parent
        form = FileModelForm()
        query_sets = models.File.objects.filter(project=request.project)
        if parent:
            # 进入了某个目录
            files = query_sets.filter(parent=parent).order_by('-file_type')
        else:
            files = query_sets.filter(parent__isnull=True).order_by('-file_type')
        return render(request, 'file.html', {'form': form, 'files': files, 'paths': paths})

    elif request.method == 'POST':
        form = FileModelForm(request=request, parent=parent, data=request.POST)
        if form.is_valid():
            form.instance.project = request.project
            form.instance.file_type = 2
            form.instance.update_user = request.authentication
            form.instance.parent = parent
            form.save()
            return JsonResponse(res.data)
        else:
            res.errors = form.errors
            res.code = 0
            res.msg = '失败'
            return JsonResponse(res.data)


def file_delete(request, pk):
    fid = request.GET.get('fid')
    models.File.objects.filter(project_id=pk, pk=fid).delete()
    res = ApiResponse()
    return JsonResponse(res.data)
