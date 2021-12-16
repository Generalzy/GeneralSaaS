from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from libs.ali_pay import settings
from alipay.aop.api.util.SignatureUtils import verify_with_rsa


def get_alipay_url(out_trade_no: str, total_amount: float, subject, body):
    """
    获取支付宝支付url
    :param out_trade_no:  商品id
    :param total_amount:  商品总价格
    :param subject:       交易名
    :param body:          交易描述
    :return:              交易url
    """
    """
    设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
    """
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = settings.GATEWAY
    alipay_client_config.app_id = settings.APPID
    alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY_STRING
    alipay_client_config.alipay_public_key = settings.ALIPAY_PUBLIC_KEY_STRING

    # 客户端对象
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
    # 对照接口文档，构造请求对象
    model = AlipayTradePagePayModel()
    # 商品编号
    model.out_trade_no = out_trade_no
    # 总价格
    model.total_amount = total_amount
    # 商品名
    model.subject = subject
    # 商品描述
    model.body = body
    # 签约
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    # 创建请求对象
    request = AlipayTradePagePayRequest(biz_model=model)
    # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段

    request.notify_url = settings.ALIPAY_NOTIFY_URL  # 设置回调通知地址（POST）
    request.return_url = settings.ALIPAY_RETURN_URL  # 设置回调通知地址（GET）

    response = client.page_execute(request, http_method='GET')
    return response


def check_pay(params):  # 定义检查支付结果的函数
    sign = params.pop('sign', None)  # 取出签名
    params.pop('sign_type')  # 取出签名类型
    params = sorted(params.items(), key=lambda e: e[0], reverse=False)  # 取出字典元素按key的字母升序排序形成列表
    message = "&".join(u"{}={}".format(k, v) for k, v in params).encode()  # 将列表转为二进制参数字符串
    try:
        status = verify_with_rsa(settings.ALIPAY_PUBLIC_KEY_STRING.encode('utf-8').decode('utf-8'), message,
                                 sign)
        # 验证签名并获取结果
        return status  # 返回验证结果
    except:  # 如果验证失败，返回假值。
        return False
