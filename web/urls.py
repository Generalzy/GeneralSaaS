"""GeneralSaaS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import url
from django.urls import re_path as url
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wikis
from web.views import files
from web.views import setting
from web.views import issues
from web.views import order

urlpatterns = [

    # 项目管理
    url(r'^project/list/', project.project_list, name='project_list'),
    # project/star/mine/1
    # project/star/join/2
    url(r'^project/star/(?P<ptype>\w+)/(?P<pk>\d+)/', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<ptype>\w+)/(?P<pk>\d+)/', project.project_unstar, name='project_unstar'),

    # 具体项目
    url(r'^manage/(?P<pk>\d+)/dashboard/chart', manage.chart, name='dashboardChart'),
    url(r'^manage/(?P<pk>\d+)/dashboard/', manage.dashboard, name='dashboard'),
    url(r'^manage/(?P<pk>\d+)/issues/detail/(?P<issue_id>\d+)/', issues.edit_issue, name='editIssue'),
    url(r'^manage/(?P<pk>\d+)/issues/record/(?P<issue_id>\d+)/', issues.record_issue, name='recordIssue'),
    url(r'^manage/(?P<pk>\d+)/issues/gencode', issues.code, name='codeIssues'),
    url(r'^issues/invite', issues.invite, name='inviteIssue'),
    url(r'^manage/(?P<pk>\d+)/issues/', issues.issues, name='issues'),
    url(r'^manage/(?P<pk>\d+)/statistics/', manage.statistics, name='statistics'),
    # file
    url(r'^manage/(?P<pk>\d+)/file/', files.file, name='file'),
    url(r'^manage/(?P<pk>\d+)/fileDelete/', files.file_delete, name='fileDelete'),
    url(r'^manage/(?P<pk>\d+)/credentials/', files.file_credentials, name='credentials'),
    url(r'^manage/(?P<pk>\d+)/filePost/', files.file_post, name='filePost'),
    url(r'^manage/(?P<pk>\d+)/fileDownload/(?P<pfile>\d+)/', files.down_load, name='fileDownload'),

    # 设置
    url(r'^settingsDelete/', setting.delete, name='settingsDelete'),
    url(r'^settings/', setting.settings, name='settings'),
    url(r'^settingsPwd/', setting.password, name='settingsPwd'),
    url(r'^settingsIssue/', setting.issue, name="settingsIssue"),
    url(r"^settingsModel/", setting.model, name="settingsModel"),
    # wiki
    url(r'^manage/(?P<pk>\d+)/wiki/', wikis.wiki, name='wiki'),
    url(r'^manage/(?P<pk>\d+)/wikiAdd/', wikis.wiki_add, name='wikiAdd'),
    url(r'^manage/(?P<pk>\d+)/wikiCatalogs/', wikis.wiki_catalogs, name='wikiCatalogs'),
    url(r'^manage/(?P<pk>\d+)/wikiDelete/(?P<wiki_pk>\d+)', wikis.wiki_delete, name='wikiDelete'),
    url(r'^manage/(?P<pk>\d+)/wikiEdit/(?P<wiki_pk>\d+)', wikis.wiki_edit, name='wikiEdit'),
    url(r'^manage/(?P<pk>\d+)/wikiUpload/', wikis.wiki_upload, name='wikiUpload'),
    # 前台路由
    url(r'^register/', account.register, name='register'),
    url(r'^sms/', account.sms, name='sms'),
    url(r'^smslogin/', account.sms_login, name='smslogin'),
    url(r'^code/', account.code, name='code'),
    url(r'^login/', account.login, name='login'),
    url(r'^logout/', account.logout, name='logout'),
    url(r'^index/', home.index),

    # 充值页面
    url('^magic/', order.pay, name='pay'),
    url('^order/', order.order, name='order'),
    url('^result/', order.pay_result, name='result'),

    # 首页
    url('^helper/',home.helper,name="helper"),
    url(r'^', home.index, name='index'),
]
