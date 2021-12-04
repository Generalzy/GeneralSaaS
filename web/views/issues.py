from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.page import Pagination
from web.forms import IssuesModelForm
from web import models
from utils.response import ApiResponse


def issues(request, pk):
    res = ApiResponse()
    if request.method == 'GET':
        current_page = request.GET.get('page')
        temp = models.Issues.objects.filter(project=request.project).all()
        all_count = temp.count()
        form = IssuesModelForm(request=request)
        page_obj = Pagination(current_page=current_page, all_count=all_count)
        data = temp[page_obj.start:page_obj.end]
        return render(request, 'issues.html', {'page_obj': page_obj, 'form': form, 'data': data})
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


def edit_issue(request, pk, issue_id):
    if request.method == 'GET':
        issue = models.Issues.objects.filter(pk=issue_id).first()
        form = IssuesModelForm(request=request,instance=issue)
        return render(request, 'issueEdit.html', {'form': form})
