
from os import environ as env
from os.path import basename

from .log import log_info


URL = 'https://storage.yandexcloud.net'


class Progress:
    def __init__(self):
        self.size = 0

    def show(self):
        mb = self.size / 1024 / 1024
        print('%.2fMB' % mb, end='\r')

    def __call__(self, chunk):
        self.size += chunk
        self.show()


class S3:
    def __init__(self, key, secret, bucket, url=URL):
        self.bucket = bucket
        self.client = get_client(key, secret, url)

    @classmethod
    def from_env(cls):
        key = env['S3_KEY']
        secret = env['S3_SECRET']
        bucket = env['S3_BUCKET']
        return cls(key, secret, bucket)

    def upload(self, path, key):
        upload(self.client, path, self.bucket, key)

    def download(self, key, path):
        download(self.client, self.bucket, key, path)


def get_client(key, secret, url):
    import boto3

    session = boto3.session.Session(
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name='us-east-1'
    )
    return session.client(
        service_name='s3',
        endpoint_url=url
    )


def upload(client, path, bucket, key):
    log_info('%s -> %s/%s', path, bucket, key)
    client.upload_file(
        Filename=path,
        Bucket=bucket,
        Key=key,
        Callback=Progress(),
        ExtraArgs={
            'StorageClass': 'COLD'
        }
    )


def download(client, bucket, key, path):
    log_info('%s/%s -> %s', bucket, key, path)
    client.download_file(
        Bucket=bucket,
        Key=key,
        Filename=path,
        Callback=Progress(),
    )


def s3_upload(args):
    key, path = args.key, args.path
    s3 = S3.from_env()
    if not key:
        key = basename(path)
    s3.upload(path, key)


def s3_download(args):
    key, path = args.key, args.path
    s3 = S3.from_env()
    if not path:
        path = basename(key)
    s3.download(key, path)
