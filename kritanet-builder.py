#! /usr/bin/env python3

#
# kritanet-builder.py
#
# Builds a Kritanet (Antinet made of Krita files) structure by batch
# conversion of Krita files into JPEG files.
#
# Outputs the structure directly into the given output directory, and creates
# the output directory, if it does not exist.
#

#
# Imports
#

import argparse
import logging
import subprocess
import os

#
# Constants
#

SCRIPT_NAME    = 'kritanet-builder.py'
SCRIPT_VERSION = '0.1.0'
SCRIPT_DATE    = '2024-10-11'

#
# Globals
#

args = None
log = logging.getLogger(__name__)

#
# Functions
#

def convert_file(in_file, out_file):
    subprocess.run(['krita', in_file, '--export', '--export-filename', out_file])

def parse_args():
    p = argparse.ArgumentParser(
            prog=f"{SCRIPT_NAME} {SCRIPT_VERSION}"
            )
    p.add_argument('-s', '--source',
                   help='Source Kritanet directory',
                   required=True)
    p.add_argument('-d', '--dest',
                   help='Destination directory for output',
                   required=True)
    p.add_argument('-w', '--overwrite',
                   help='Overwrite existing output dir',
                   action='store_true')

    global args
    args = p.parse_args()

def walk_directory(path, dest):
    path = path.rstrip('/')

    for root, dirs, files in os.walk(path):
        log.debug(f"Walking '{root}'")

        subpath = ''
        newpath = dest.rstrip('/')
        if root != path:
            subpath = root.removeprefix(path)
            #newpath = os.path.join(dest, subpath)
            newpath += subpath
            log.debug(f"Create dir '{newpath}'")
            os.makedirs(newpath, exist_ok=True)

        for file in files:
            if file.endswith('.kra'):
                #log.debug(f"Found Krita file '{file}'")
                file_name = file.removesuffix('.kra') + '.jpg'
                full_oldfile = os.path.join(root, file)
                oldfile = os.path.join(subpath, file)
                newfile = os.path.join(newpath, file_name)

                convert = False
                if os.path.exists(newfile):
                    if os.path.getmtime(full_oldfile) > os.path.getmtime(newfile):
                        log.debug(f"File '{newfile}' is out of date.")
                        convert = True
                    else:
                        log.debug(f"File '{newfile}' is current.")
                else:
                    convert = True

                if convert:
                    log.debug(f"Convert '{oldfile}' to '{newfile}'")
                    convert_file(full_oldfile, newfile)

#
# MAIN
#

if __name__ == '__main__':
    parse_args()
    logging.basicConfig(level=logging.DEBUG)

    log.debug(f"Source structure: '{args.source}'")
    log.debug(f"Output structure: '{args.dest}'")

    if args.overwrite:
        os.makedirs(args.dest, exist_ok=True)
    else:
        os.makedirs(args.dest)

    walk_directory(args.source, args.dest)
