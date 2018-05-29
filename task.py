#!/usr/bin/python3
import importlib
import os

import sys

TASK_FOLDER = os.path.abspath(os.path.join(os.curdir, 'task'))

if len(sys.argv) < 2:
    print('no script name provided')

task = sys.argv[1]

filePath = os.path.join(TASK_FOLDER, task + '.py')
if not os.path.isfile(filePath):
    print('task not found {}'.format(filePath))

importlib.import_module('task.' + task)
