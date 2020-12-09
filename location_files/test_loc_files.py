#!/usr/bin/env python
import os

from gnome.persist import load

'''
very simple script to test if location files load
'''

loc_files = os.path.dirname(os.path.abspath(__file__))
dirs = os.listdir(loc_files)

for d in dirs:
    save_dir = os.path.join(d, '{0}_save'.format(d))
    model = os.path.join(loc_files, save_dir, 'Model.json')

    if not os.path.exists(model):
        continue

    try:
        m = load(model)
        print("successfully loaded: {0}".format(model))
    except:
        print("FAILED: {0}".format(model))
