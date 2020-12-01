# -*- coding: utf-8 -*-

import os

import mock
import pytest
from pyramid import compat

from pyramid_storage.s3v2 import S3V2FileStorage


class MockBucket(mock.Mock):

    def list(self, prefix, delimiter):

        mock_key_1 = mock.Mock
        mock_key_1.name = 'image1.png'

        return [mock_key_1]


class MockS3Resource(object):

    def Bucket(self, bucket_name):
        return MockBucket()


class MockS3Connection(object):

    def get_bucket(self, bucket_name):
        return MockBucket()


def _get_mock_s3_connection(self):
    return MockS3Connection()


def _get_mock_s3_resource(self):
    return MockS3Resource()


def _mock_open_name():

    if compat.PY3:
        return 'builtins.open'
    else:
        return '__builtin__.open'


def _mock_open(name='test', mode='wb'):

    obj = mock.Mock()
    obj.__enter__ = mock.Mock()
    obj.__enter__.return_value = mock.Mock()
    obj.__exit__ = mock.Mock()
    return obj


def test_save_if_file_not_allowed():
    from pyramid_storage import s3v2
    from pyramid_storage.exceptions import FileNotAllowed

    fs = mock.Mock()
    fs.filename = "test.zip"

    settings = {
                'storage.aws.access_key': 'abc',
                'storage.aws.secret_key': '123',
                'storage.aws.bucket_name': 'Attachments',
                'storage.aws.is_secure': 'false',
                'storage.aws.host': 'localhost',
                'storage.aws.port': '5000',
                'storage.aws.use_path_style': 'true',
                'storage.aws.num_retries': '3',
                'storage.aws.timeout': '10',
                'storage.aws.signature_version': 's3v4',
                'storage.aws.extensions': 'documents'
    }

    s = s3v2.S3V2FileStorage.from_settings(settings, 'storage.')

    with mock.patch(
            'pyramid_storage.s3v2.S3V2FileStorage.get_resource',
            _get_mock_s3_resource):

        with pytest.raises(FileNotAllowed):
            s.save(fs)


def test_save_if_file_allowed():
    from pyramid_storage import s3v2

    fs = mock.Mock()
    fs.filename = "test.jpeg"

    settings = {
                'storage.aws.access_key': 'abc',
                'storage.aws.secret_key': '123',
                'storage.aws.bucket_name': 'Attachments',
                'storage.aws.is_secure': 'false',
                'storage.aws.host': 'localhost',
                'storage.aws.port': '5000',
                'storage.aws.use_path_style': 'true',
                'storage.aws.num_retries': '3',
                'storage.aws.timeout': '10',
                'storage.aws.signature_version': 's3v4',
                'storage.aws.extensions': 'default'
            }
    s = s3v2.S3V2FileStorage.from_settings(settings, 'storage.')

    with mock.patch(
            'pyramid_storage.s3v2.S3V2FileStorage.get_resource',
            _get_mock_s3_resource):

        s.save(fs)


def test_save_file():
    from pyramid_storage import s3v2

    settings = {
        'storage.aws.access_key': 'abc',
        'storage.aws.secret_key': '123',
        'storage.aws.bucket_name': 'Attachments',
        'storage.aws.is_secure': 'false',
        'storage.aws.host': 'localhost',
        'storage.aws.port': '5000',
        'storage.aws.use_path_style': 'true',
        'storage.aws.num_retries': '3',
        'storage.aws.timeout': '10',
        'storage.aws.signature_version': 's3v4',
        'storage.aws.extensions': 'default'
    }

    s = s3v2.S3V2FileStorage.from_settings(settings, 'storage.')

    with mock.patch(
            'pyramid_storage.s3v2.S3V2FileStorage.get_resource',
            _get_mock_s3_resource):
        name = s.save_file(mock.Mock(), "test.jpg")
        assert name == "test.jpg"


def test_save_if_randomize():
    from pyramid_storage import s3v2

    fs = mock.Mock()
    fs.filename = "test.jpg"

    settings = {
        'storage.aws.access_key': 'abc',
        'storage.aws.secret_key': '123',
        'storage.aws.bucket_name': 'Attachments',
        'storage.aws.is_secure': 'false',
        'storage.aws.host': 'localhost',
        'storage.aws.port': '5000',
        'storage.aws.use_path_style': 'true',
        'storage.aws.num_retries': '3',
        'storage.aws.timeout': '10',
        'storage.aws.signature_version': 's3v4',
        'storage.aws.extensions': 'default'
    }

    s = s3v2.S3V2FileStorage.from_settings(settings, 'storage.')

    with mock.patch(
            'pyramid_storage.s3v2.S3V2FileStorage.get_resource',
            _get_mock_s3_resource):
        name = s.save(fs, randomize=True)
    assert name != "test.jpg"


def test_open_simple_case():

    from pyramid_storage import s3v2

    s = s3v2.S3FileStorage(
        access_key="AK",
        secret_key="SK",
        bucket_name="my_bucket",
        extensions="images")

    with mock.patch('pyramid_storage.s3.S3FileStorage.get_connection',
                    _get_mock_s3_connection):
        tmp_file = s.open('foo')

    assert os.path.isfile(tmp_file.name) is True

    with tmp_file:
        # just to ensure the fill will not be deleted
        pass

    assert os.path.isfile(tmp_file.name) is True


def test_open_as_context_manager():

    from pyramid_storage import s3v2

    s = s3v2.S3FileStorage(
        access_key="AK",
        secret_key="SK",
        bucket_name="my_bucket",
        extensions="images")

    with mock.patch('pyramid_storage.s3.S3FileStorage.get_connection',
                    _get_mock_s3_connection):
        with s.open('foo', delete=True) as f:
            tmp_file_name = f.name
            assert os.path.isfile(tmp_file_name) is True

    assert os.path.isfile(tmp_file_name) is False


def test_s3v2_open_should_open_image_in_bucket(mock_boto_s3, image_in_bytes):

    s = S3V2FileStorage.from_settings({'storage.aws.bucket_name': 'my_bucket'}, 'storage.')

    with s.open('filename', delete=True) as image:
        assert image.read() == image_in_bytes


def test_s3v2_get_md5(mock_boto_s3, image_in_bytes):
    from pyramid_storage import s3v2

    settings = {
        'storage.aws.access_key': 'abc',
        'storage.aws.secret_key': '123',
        'storage.aws.bucket_name': 'my_bucket',
        'storage.aws.is_secure': 'false',
        'storage.aws.host': 'localhost',
        'storage.aws.port': '5000',
        'storage.aws.use_path_style': 'true',
        'storage.aws.num_retries': '3',
        'storage.aws.timeout': '10',
        'storage.aws.signature_version': 's3v4',
        'storage.aws.extensions': 'default'
    }

    s = s3v2.S3V2FileStorage.from_settings(settings, 'storage.')

    mock_boto_s3.put_object(Bucket="my_bucket", Key="filename", Body="test")
    resulting_hash = s.get_md5("filename")

    assert resulting_hash == '098f6bcd4621d373cade4e832627b4f6'
