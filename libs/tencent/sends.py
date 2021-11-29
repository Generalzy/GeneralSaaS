from qcloudsms_py import SmsSingleSender
from libs.tencent import conf


def send_message(phone, code):
    ssender = SmsSingleSender(conf.appid, conf.appkey)
    params = [code, '2']
    result = ssender.send_with_param(86, phone, conf.template_id, params, sign=conf.sms_sign, extend="", ext="")
    if not result.get('result'):
        return True
    return False
