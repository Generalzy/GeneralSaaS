from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, HttpResponse
from web.forms import FileModelForm, FileForm
from web import models
from libs.tencent.cos import delete_file, delete_files, credentials
from django.views.decorators.csrf import csrf_exempt
import json


# url: http://127.0.0.1:8000/manage/6/file/?folder=8
# url: http://127.0.0.1:8000/manage/project(id)/file/?folder=folder(id)
def file(request, pk):
    res = ApiResponse()
    folder = request.GET.get('folder', None)  # type:str
    if folder and folder.isdigit():
        # 只有文件夹可以点进去
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
        return render(request, 'file.html', {'form': form, 'files': files, 'paths': paths, 'parent': parent})

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
    bucket = request.project.bucket
    file_obj = models.File.objects.filter(project_id=pk, pk=fid).first()
    if file_obj.file_type == 1:
        # 删除文件
        # 删除后还要归还size
        request.project.use_space -= file_obj.size
        request.project.save()
        # 去cos中删除文件
        data = delete_file(bucket=bucket, key=file_obj.key)
    else:
        # 删除文件夹
        # 要递归删除所有文件并归还所有size
        folder_list = [file_obj, ]
        total_size = 0
        key_list = []
        for folder in folder_list:
            child_list = models.File.objects.filter(parent=folder, project_id=pk).order_by('-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    total_size += child.size
                    key_list.append({'Key': child.key})

        if total_size:
            request.project.use_space -= total_size
            request.project.save()
        if key_list:
            data = delete_files(bucket=bucket, keys=key_list)

    file_obj.delete()
    res = ApiResponse()
    return JsonResponse(res.data)


@csrf_exempt
def file_credentials(request, pk):
    # request我放进去了price,user,project
    res = ApiResponse()
    if request.method == 'POST':
        single_size = request.price.per_file_size * 1024 * 1024  # 转为字节
        space = request.price.project_space * 1024 * 1024 * 1024  # 转为字节
        total_size = 0  # 字节

        checkFiles = json.loads(request.body)
        for item in checkFiles:
            if item.get('size') > single_size:
                res.code = 0
                res.msg = f'{item.get("name")}超出限制(最大{single_size}Mb),请升级套餐'
                return JsonResponse(res.data)
            elif len(item.get('name')) > 32:
                res.code = 0
                res.msg = f'{item.get("name")}文件名过长'
            else:
                total_size += item.get('size')
        use_space = request.project.use_space * 1024 * 1024 * 1024  # 转为字节
        if use_space + total_size > space:
            res.code = 0
            res.msg = '项目容量超额，请升级套餐'
            return JsonResponse(res.data)

        data = credentials(bucket=request.project.bucket)
        res.tmp = data
        return JsonResponse(res.data)


@csrf_exempt
def file_post(request, pk):
    data = json.loads(request.body)
    form = FileForm(request=request, data=data)
    res = ApiResponse()
    if form.is_valid():
        data_dic = form.cleaned_data
        data_dic.pop('etag')
        data_dic.update({
            'project': request.project,
            'file_type': 1,
            'update_user': request.authentication
        })
        instance = models.File.objects.create(**data_dic)
        res.id = instance.id
        res.name = instance.name
        res.size = instance.size
        res.updatedatetime = instance.update_datetime
        res.username = instance.update_user.username
        return JsonResponse(res.data)
    else:
        res.code = 0
        res.msg = form.errors
        return JsonResponse(res.data)


def down_load(request, pk, pfile):
    if request.method == 'GET':
        import requests
        from django.utils.encoding import escape_uri_path
        file_obj = models.File.objects.filter(pk=pfile).first()
        res = requests.get(file_obj.path)
        response = HttpResponse(res.iter_content(), content_type='application/octet-stream')
        response['Content-Disposition'] = f"attachment;filename={escape_uri_path(file_obj.name)}"
        return response
