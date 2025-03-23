import os
import sys
from os.path import dirname
from sys import path

path.append(dirname(__file__))


def django_manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
