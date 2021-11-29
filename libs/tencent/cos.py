from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from . import conf

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
