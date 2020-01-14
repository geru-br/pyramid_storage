# -*- coding: utf-8 -*-

import boto3
import pytest
from moto import mock_s3


@pytest.fixture
def mock_boto_s3():
    """Mock boto3 using moto with an image stored in the bucket."""
    with mock_s3():
        s3 = boto3.resource("s3")
        s3.create_bucket(Bucket="my_bucket")
        bucket = s3.Bucket("my_bucket")
        file_object = bucket.Object("filename")
        with open("tests/fixtures/image.png", "rb") as f:
            file_object.upload_fileobj(f)

        yield boto3.client("s3")

        for key in bucket.objects.all():
            key.delete()

        bucket.delete()


@pytest.fixture
def image_in_bytes():
    with open("tests/fixtures/image.png", "rb") as f:
        data = f.read()
    return data
