from django.template import Library
from web import models
from django.urls import reverse

register = Library()


@register.inclusion_tag('inclusion_tags/projects.html')
def all_project(request):
    # 获取所有创建的
    mine_projects = models.Project.objects.filter(creator=request.authentication)
    # 创建所有参与的
    join_user_projects = models.ProjectUser.objects.filter(user=request.authentication)
    return {'mine_projects': mine_projects, 'join_user_projects': join_user_projects, 'request': request}


@register.inclusion_tag('inclusion_tags/menu_list.html')
def all_menu_list(request):
    menu_list = [
        {'title': '概览', 'url': reverse("dashboard", kwargs={'pk': request.project.id})},
        {'title': '问题', 'url': reverse("issues", kwargs={'pk': request.project.id})},
        {'title': '统计', 'url': reverse("statistics", kwargs={'pk': request.project.id})},
        {'title': 'wiki', 'url': reverse("wiki", kwargs={'pk': request.project.id})},
        {'title': '文件', 'url': reverse("file", kwargs={'pk': request.project.id})},
        # {'title': '设置', 'url': reverse("settings", kwargs={'pk': request.project.id})}
    ]
    for item in menu_list:
        current_url = request.path_info  # type:str
        if current_url.startswith(item['url']):
            item['style'] = "color:white"

    return {'menu_list': menu_list}


def get_size(value, v):
    return f'{value / v:.3}'


register.filter('get_size', get_size)
