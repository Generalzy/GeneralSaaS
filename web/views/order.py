from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from libs.ali_pay import get_alipay_url, check_pay
import uuid
from web import models
from utils.response import ApiResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from json import dumps, loads
import datetime


def pay(request):
    if request.method == "GET":
        prices = models.PricePolicy.objects.filter(category=2).all()
        return render(request, 'pay.html', {'prices': prices})
    elif request.method == 'POST':
        price_policy = request.POST.get('pid')
        obj = models.PricePolicy.objects.filter(pk=price_policy).first()
        count = request.POST.get('count')  # type:str
        if not count.isdigit() or int(count) <= 0:
            return redirect('pay')
        elif not obj:
            return redirect('pay')
        else:
            out_trade_no = str(uuid.uuid4())
            order_dic = {
                'out_trade_no': out_trade_no,
                'subject': obj.title,
                'price': int(count) * obj.price,
                'count': count,
                'single_price': obj.price,
                'price_policy': price_policy,
                'body': f'{request.authentication.id}|{out_trade_no}'
            }
            cache.set(f'{request.authentication.id}-order-detail', dumps(order_dic), 30 * 60)
            return render(request, 'order.html', {'order_dic': order_dic})


@csrf_exempt
def order(request):
    if request.method == 'POST':
        res = ApiResponse()
        order_dic = loads(cache.get(f'{request.authentication.id}-order-detail'))
        out_trade_no = order_dic.get('out_trade_no')
        total_amount = order_dic.get('price')
        subject = order_dic.get('subject')
        count = order_dic.get('count')
        price_policy = order_dic.get('price_policy')
        body = order_dic.get('body')
        try:
            url = get_alipay_url(out_trade_no, total_amount, subject, body)
            res.url = url
            models.Transaction.objects.create(status=1, order=out_trade_no, count=count, price=total_amount,
                                              start_datetime=datetime.datetime.now(),
                                              end_datetime=datetime.datetime.now() + datetime.timedelta(days=365),
                                              user=request.authentication, price_policy_id=price_policy)
        except Exception as e:
            res.code = 0
            res.msg = e
        return JsonResponse(res.data)


# 同步通知会在支付完成后，跳转到回调通知地址页面，并以GET方式传递参数。
# 异步通知会在支付完成后，向回调通知地址发出POST请求，同时传递参数字典。
@csrf_exempt
def pay_result(request):  # 定义处理回调通知的函数
    if request.method == 'GET':
        params = request.GET.dict()  # 获取参数字典
        # get: <QueryDict: {'charset': ['utf-8'], 'out_trade_no': ['72296bc3-4155-4150-90ad-208d5f03490e'],
        # 'method': ['alipay.trade.page.pay.return'], 'total_amount': ['200.00'], 'sign': [
        # 'XP6nYNN3CCsrAZunK8eKh+uVHot9UE3Bw99AVVUjB1IqtvFnF0zNPxGRB5c8hW5V
        # +O3OE67U9zCJwp3Jbd87SbZyVnFKopTSl1pji23ZrSXZatGH6eqzMKrcMNAZBNvhcgnG/eZB3yCF76G1j8k10hbO18t
        # /zGGTpdEIuvM2KOtcj3o3GjKKhwaV2jEHHJ0OSw0ciHg9U5T1gWO0L/6Qmkw+xq1EOePsjEYj4iNDWqzH2/FJ60najVhU4dKmLOYC
        # +br0UpZBeIBRmqgrV2Akw3guZQImtpxUXIIM10VjzHl0uklKv9971rk33Zzj/TrUEdd8xZsKGQpRhkniWHQIqA=='], 'trade_no': [
        # '2021121522001480040501263817'], 'auth_app_id': ['2021000118621457'], 'version': ['1.0'], 'app_id': [
        # '2021000118621457'], 'sign_type': ['RSA2'], 'seller_id': ['2088621956491045'], 'timestamp': ['2021-12-15
        # 18:49:52']}>
        out_trade_no = params.get('out_trade_no')
        if check_pay(params):  # 调用检查支付结果的函数
            '''
                此处编写支付成功后的业务逻辑
            '''
            return render(request, 'pay_success.html', {'out_trade_no': out_trade_no})
        else:
            '''
                此处编写支付失败后的业务逻辑
            '''
            return render(request, 'pay_failed.html', {'out_trade_no': out_trade_no})
    if request.method == 'POST':
        params = request.POST.dict()  # 获取参数字典
        # post: <QueryDict: {'gmt_create': ['2021-12-15 18:49:27'], 'charset': ['utf-8'], 'gmt_payment': ['2021-12-15
        # 18:49:33'], 'notify_time': ['2021-12-15 18:49:34'], 'subject': ['SVIP'], 'sign': [
        # 'hjDZ0f54GmprBAWGorqMpL/GzJ6naAqyH5dEN0wfNP+nUP8qSVCnSTSPR20SPs3/l5JcIBElytUP5
        # +aVy8mJDHRY4W9Y6mNnlY8ADJgwIOyVVDAllso+gc93RdccyzqkSn+uSgXMd/RAtTizVshrwtgMT9AyRzuUFEB19OshT4Rh8yij5
        # +VcAxRVermf1I8pgcpDucfHFecsueHLti4N+DIeQSQ8WdtUlvlfaygwXPLV+QmPFf8fBTgi5i5sKyWVZojVmkKXi86TR0h2PPmGswgvUJ
        # +gcx/ZzqtMmCYNAflP0iqvazdR/61fPS5PVmlugaV+fyB8QE/ICl6aKV47nA=='], 'buyer_id': ['2088622956680044'],
        # 'body': ['SVIP'], 'invoice_amount': ['200.00'], 'version': ['1.0'], 'notify_id': [
        # '2021121500222184934080040516113838'], 'fund_bill_list': ['[{"amount":"200.00",
        # "fundChannel":"ALIPAYACCOUNT"}]'], 'notify_type': ['trade_status_sync'], 'out_trade_no': [
        # '72296bc3-4155-4150-90ad-208d5f03490e'], 'total_amount': ['200.00'], 'trade_status': ['TRADE_SUCCESS'],
        # 'trade_no': ['2021121522001480040501263817'], 'auth_app_id': ['2021000118621457'], 'receipt_amount': [
        # '200.00'], 'point_amount': ['0.00'], 'app_id': ['2021000118621457'], 'buyer_pay_amount': ['200.00'],
        # 'sign_type': ['RSA2'], 'seller_id': ['2088621956491045']}>

        if check_pay(params):  # 调用检查支付结果的函数
            '''
                此处编写支付成功后的业务逻辑
                订单表加数据，用户权限升级
            '''
            body = params.get('body').split('|')  # ['8','e8e36775-7b48-4b71-b9f7-ae316ae25d10']
            trans_obj = models.Transaction.objects.filter(user_id=int(body[0]), order=body[-1]).first()
            trans_obj.status = 2
            trans_obj.save()
            return HttpResponse('success')  # 返回成功信息到支付宝服务器,必须返回success
