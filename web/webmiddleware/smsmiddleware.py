from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from utils.response import ApiResponse
from django.http import JsonResponse


class SmsMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        if request.path_info == '/sms/':
            phone = request.POST.get('phone')
            redis_code = cache.get(f'{settings.PHONE_CACHE_KEY}{phone}')
            if redis_code:
                res = ApiResponse(code=0, msg='请勿重复获取验证码')
                return JsonResponse(res.data)
