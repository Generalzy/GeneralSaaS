from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime


class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        username = request.session.get('username', None)
        user_obj = models.UserInfo.objects.filter(username=username).first()
        request.authentication = user_obj


class LoginMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info in settings.WHITE_URL_LIST:
            return
        else:
            if not request.authentication:
                return redirect('smslogin')
            else:
                identity = models.Transaction.objects.filter(user=request.authentication, status=2).order_by(
                    '-id').first()
                current = datetime.now()
                if identity.end_datetime and identity.end_datetime < current:
                    # 过期了就设置成普通身份
                    identity = models.Transaction.objects.filter(user=request.authentication, status=2,
                                                                 price_policy__category=1).first()
                request.price = identity.price_policy

    def process_view(self, request, view, *args, **kwargs):
        if not request.path_info.startswith('/manage/'):
            return

        pk = args[-1].get('pk')
        # 我创建的项目
        # 把项目对象也添加到request中
        project_obj = models.Project.objects.filter(creator=request.authentication, pk=pk).first()
        if project_obj:
            request.project = project_obj
            return

        # 我参与的项目
        uproject_obj = models.Project.objects.filter(user=request.authentication, project_id=pk).first()
        if uproject_obj:
            request.project = uproject_obj.project
            return

        return redirect('project_list')
