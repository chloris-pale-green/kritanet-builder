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
SCRIPT_VERSION = '0.2.0'
SCRIPT_DATE    = '2024-10-12'

#
# Globals
#

log = logging.getLogger(__name__)

#
# Classes
#

class KritanetPaths:
    def __init__(self):
        # Absolute path to the source root dir
        self.src_root = None
        # Absolute path to the destination root dir
        self.dst_root = None
        # Relative paths of all directories in the source Kritanet
        self.src_dirs = []
        # Relative paths of all cards (.kra) in the source Kritanet
        self.src_cards = []
        # Relative paths of all currently present directories in the destination Kritanet
        self.dst_dirs = []
        # Relative paths of all currently present cards (.jpg) in the destination Kritanet
        self.dst_cards = []

#
# Functions
#

def convert_file(in_file, out_file):
    res = subprocess.run(
        ['krita', in_file, '--export', '--export-filename', out_file],
        capture_output=True)
    res.check_returncode()

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
    p.add_argument('-v', '--verbose',
        help='Include debug output',
        action='store_true')

    return p.parse_args()

def walk_src_root(path, kritanet_paths_ref):
    path = path.rstrip('/')
    kritanet_paths_ref.src_root = path

    log.debug(f"Walking source root '{path}'")
    for root, dirs, files in os.walk(path):
        root = root.rstrip('/')
        relpath = root.removeprefix(path + '/')
        log.debug(f"Entering '{relpath}'")

        if root != path:
            kritanet_paths_ref.src_dirs.append(relpath)
        else:
            relpath = ''
        
        for file in files:
            if file.endswith('.kra'):
                cardpath = os.path.join(relpath, file)
                kritanet_paths_ref.src_cards.append(cardpath)

def walk_dst_root(path, kritanet_paths_ref):
    path = path.rstrip('/')
    kritanet_paths_ref.dst_root = path

    if not os.path.isdir(path):
        log.debug(f"Destination root '{path}' does not yet exist")
        return

    log.debug(f"Walking destination root '{path}'")
    for root, dirs, files in os.walk(path):
        root = root.rstrip('/')
        relpath = root.removeprefix(path + '/')
        log.debug(f"Entering '{relpath}'")

        if root != path:
            kritanet_paths_ref.dst_dirs.append(relpath)
        else:
            relpath = ''
        
        for file in files:
            cardpath = os.path.join(relpath, file)
            if file.endswith('.jpg'):
                kritanet_paths_ref.dst_cards.append(cardpath)
            else:
                log.warn(f"Unknown file in destination root: '{cardpath}'")

def equalise_roots(kritanet_paths):
    # Create copies of collections, that will be modified
    unaccounted_dst_dirs = [dir for dir in kritanet_paths.dst_dirs]
    unaccounted_dst_cards = [card for card in kritanet_paths.dst_cards]

    # Equalise directories

    for src_dir in kritanet_paths.src_dirs:
        if src_dir in unaccounted_dst_dirs:
            log.debug(f"Directory '{src_dir}' already exists")
            unaccounted_dst_dirs.remove(src_dir)
        else:
            dirpath = os.path.join(kritanet_paths.dst_root, src_dir)
            log.debug(f"Creating directory '{dirpath}'")
            os.makedirs(dirpath)
    
    if len(unaccounted_dst_dirs) > 0:
        log.warning(f"Unaccounted destination directories: {unaccounted_dst_dirs}")
    
    # Find exisisting cards

    log.debug('Finding existing cards')
    cards_to_make = []

    for card in kritanet_paths.src_cards:
        jpg_card = rename_kra_to_jpg(card)
        sc = os.path.join(kritanet_paths.src_root, card)
        dc = os.path.join(kritanet_paths.dst_root, jpg_card)
        if jpg_card in unaccounted_dst_cards:
            unaccounted_dst_cards.remove(jpg_card)
            if os.path.getmtime(sc) > os.path.getmtime(dc):
                log.debug(f"Outdated card: '{dc}'")
                cards_to_make.append(card)
            else:
                log.debug(f"Card '{dc}' is up to date")
        else:
            log.debug(f"Missing card: '{dc}'")
            cards_to_make.append(card)
    
    if len(cards_to_make) > 0:
        log.debug(f"Cards to make: {cards_to_make}")
    if len(unaccounted_dst_cards) > 0:
        log.warning(f"Unaccounted cards: {unaccounted_dst_cards}")
    
    # Make new cards

    cards_made = 0
    for card in cards_to_make:
        jpg_card = rename_kra_to_jpg(card)
        sc = os.path.join(kritanet_paths.src_root, card)
        dc = os.path.join(kritanet_paths.dst_root, jpg_card)

        percent = 100 * cards_made / len(cards_to_make)

        log.debug(f"Converting: '{sc}' -> '{dc}")
        log.info(f"{cards_made}/{len(cards_to_make)} ({percent:3.0f}%): {dc}")
        convert_file(sc, dc)

        cards_made += 1

def rename_kra_to_jpg(path):
    return path.removesuffix('.kra') + '.jpg'

#
# MAIN
#

if __name__ == '__main__':
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    log.debug(f"Source root: '{args.source}'")
    log.debug(f"Output root: '{args.dest}'")

    os.makedirs(args.dest, exist_ok=True)

    kritanet_paths = KritanetPaths()

    walk_src_root(args.source, kritanet_paths)
    walk_dst_root(args.dest, kritanet_paths)

    if args.verbose:
        print('BEGIN KRITANET PATHS')
        from pprint import pp
        pp(vars(kritanet_paths))
        print('END KRITANET PATHS')

    log.info(f"Found {len(kritanet_paths.src_cards)} source and {len(kritanet_paths.dst_cards)} existing cards")
    log.info('Equalising source and destination directories')
    equalise_roots(kritanet_paths)
    log.info('Equalising done')