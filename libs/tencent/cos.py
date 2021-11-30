from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from . import conf
from sts.sts import Sts
from json import dumps

region = 'ap-nanjing'
config = CosConfig(Region=conf.region, SecretId=conf.secret_id, SecretKey=conf.secret_key)

client = CosS3Client(config)


def upload_file(bucket, key, body):
    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Key=key,
        Body=body
    )
    return response


def create_bucket(bucket):
    client.create_bucket(Bucket=bucket, ACL='public-read')
    client.put_bucket_cors(Bucket=bucket, CORSConfiguration=conf.CORS_CONFIG)


def delete_file(bucket, key):
    return client.delete_object(Bucket=bucket, Key=key)


def delete_files(bucket, keys):
    objects = {
        "Quiet": "true",
        "Object": keys
    }

    return client.delete_objects(Bucket=bucket, Delete=objects)


def credentials(bucket):
    credentials_config = {
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 300,
        'secret_id': conf.secret_id,
        # 固定密钥
        'secret_key': conf.secret_key,
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': conf.region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            'name/cos:PostObject',
            # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
        ],

    }

    sts = Sts(credentials_config)
    response = sts.get_credential()
    return dict(response)


def auth(bucket, key):
    return client.head_object(Bucket=bucket, Key=key)
