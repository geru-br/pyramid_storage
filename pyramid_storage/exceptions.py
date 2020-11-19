# -*- coding: utf-8 -*-


class FileNotAllowed(Exception):
    """
    Thrown if file does not have an allowed extension.
    """


class ResourceNotFound(Exception):
    """
    Thrown if file resource is not found at a given path
    """