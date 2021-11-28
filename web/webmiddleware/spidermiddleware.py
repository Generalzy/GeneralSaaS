from django.utils.deprecation import MiddlewareMixin
import re
from django.http import JsonResponse
from utils.response import ApiResponse

BLACK_ADDR_LIST = []


class SpiderMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
        else:
            remote_addr = request.META.get('REMOTE_ADDR')

        if remote_addr not in BLACK_ADDR_LIST:
            request_ua = request.META.get('HTTP_USER_AGENT')
            if re.search(r'^.*python.*', request_ua):
                BLACK_ADDR_LIST.append(remote_addr)
                res = ApiResponse(code=0, msg='本站禁止爬虫，您的ip已被拉黑')
                return JsonResponse(res.data)
            else:
                return
        else:
            res = ApiResponse(code=0, msg='本站禁止爬虫，您的ip已被拉黑')
            return JsonResponse(res.data)
