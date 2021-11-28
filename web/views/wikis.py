from django.http import JsonResponse
from utils.response import ApiResponse
from django.shortcuts import render, redirect
from web.forms import WikiModelForm
from django.urls import reverse
from web import models
from django.views.decorators.csrf import csrf_exempt
from libs.tencent.cos import upload_file
from utils.secret import get_key


def wiki(request, pk):
    if request.method == 'GET':
        wiki_id = request.GET.get('wiki_id')  # type:str
        if wiki_id and wiki_id.isdigit():
            wiki_data = models.Wiki.objects.filter(pk=wiki_id, project=pk).values('id', 'title', 'content').first()
            return render(request, 'wiki.html', {'wiki_data': wiki_data})
        else:
            return render(request, 'wiki.html')


def wiki_add(request, pk):
    if request.method == 'GET':
        form = WikiModelForm(request=request)
        return render(request, 'wiki_add.html', {'form': form})
    elif request.method == 'POST':
        form = WikiModelForm(request=request, data=request.POST)
        if form.is_valid():
            # 判断用户是否选择了父文章
            # <class 'web.models.Wiki'>
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            form.instance.project = request.project
            form.save()
            url = reverse('wiki', kwargs={'pk': pk})
            return redirect(url)
        else:
            res = ApiResponse()
            res.errors = form.errors
            return JsonResponse(res.data)


def wiki_catalogs(request, pk):
    data = models.Wiki.objects.filter(project=request.project).values_list('id', 'title', 'parent').order_by('depth',
                                                                                                             'id')
    res = ApiResponse()
    res.info = list(data)
    return JsonResponse(res.data)


def wiki_delete(request, pk, wiki_pk):
    if request.method == 'GET':
        models.Wiki.objects.filter(pk=wiki_pk, project_id=pk).delete()
        url = reverse('wiki', kwargs={'pk': pk})
        return redirect(url)


def wiki_edit(request, pk, wiki_pk):
    wiki_obj = models.Wiki.objects.filter(pk=wiki_pk, project=pk).first()
    if request.method == 'GET':
        form = WikiModelForm(request=request, instance=wiki_obj)
        return render(request, 'wiki_add.html', {'form': form})
    if request.method == 'POST':
        form = WikiModelForm(request=request, instance=wiki_obj, data=request.POST)
        if form.is_valid():
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            form.instance.project = request.project
            form.save()
            url = reverse('wiki', kwargs={'pk': pk})
            return redirect(f'{url}?wiki_id={wiki_pk}')


@csrf_exempt
def wiki_upload(request, pk):
    img_obj = request.FILES.get('editormd-image-file')
    img_ext = img_obj.name.rsplit('.')[-1]
    project_obj = models.Project.objects.filter(pk=pk, creator=request.authentication).first()
    key = f'{get_key()}.{img_ext}'
    res = upload_file(
        bucket=project_obj.bucket,
        body=img_obj,
        key=key
    )
    response = ApiResponse()
    if res:
        response.success = 1
        response.message = None
        response.url = f'https://{project_obj.bucket}.cos.ap-nanjing.myqcloud.com/{key}'
        return JsonResponse(response.data)
    else:
        response.success = 0
        response.message = '上传错误，请重新上传'
        response.url = None
        return JsonResponse(response.data)
