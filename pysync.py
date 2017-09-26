#!/usr/bin/python
from __future__ import print_function
import os
import os.path
import shutil
from argparse import ArgumentParser
from hashlib import sha1

parser = ArgumentParser()

parser.add_argument(
    '-c', '--chunk-size', type=int, default=65535,
    help='The chunk size for reading files'
)

parser.add_argument('source', help='Directory which contains master data')

parser.add_argument('destination', help='The directory to sync with source')


def test_digests(source, dest):
    """Return whether or not the sources of file source and file dest are
    equal."""
    return get_digest(source) == get_digest(dest)


def get_ambiguous_path(base, source):
    """Return base with source removed."""
    return base[len(source) + 1:]


def get_digest(path):
    """Return the digest for the file at path."""
    sum = sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(args.chunk_size)
            if data:
                sum.update(data)
            else:
                break
    return sum.digest()


if __name__ == '__main__':
    args = parser.parse_args()
    if not os.path.isdir(args.source):
        print('Error: Source directory does not exist.')
        raise SystemExit
    elif not os.path.isdir(args.destination):
        print('Error: Destination directory does not exist.')
        raise SystemExit
    else:
        print('Syncing %s -> %s.' % (args.source, args.destination))
    for base, directories, files in os.walk(args.destination):
        ambiguous_path = get_ambiguous_path(base, args.destination)
        for directory in directories:
            source_dir = os.path.join(args.source, ambiguous_path, directory)
            dest_dir = os.path.join(base, directory)
            if not os.path.isdir(source_dir):
                print('Deleting directory %s.' % dest_dir)
                shutil.rmtree(dest_dir)
        for filename in files:
            source_file = os.path.join(args.source, ambiguous_path, filename)
            dest_file = os.path.join(base, filename)
            if not os.path.isfile(source_file):
                print('Deleting file %s.' % dest_file)
                os.remove(dest_file)
    for base, directories, files in os.walk(args.source):
        ambiguous_path = get_ambiguous_path(base, args.source)
        for directory in directories:
            source_dir = os.path.join(base, directory)
            dest_dir = os.path.join(
                args.destination, ambiguous_path, directory
            )
            print('%s... ' % os.path.join(ambiguous_path, directory), end='')
            if not os.path.isdir(dest_dir):
                print('Creating.')
                os.makedirs(dest_dir)
            else:
                print('Present.')
        for filename in files:
            source_file = os.path.join(base, filename)
            dest_file = os.path.join(
                args.destination, ambiguous_path, filename
            )
            print('%s: ' % os.path.join(ambiguous_path, filename), end='')
            if os.path.isfile(dest_file):
                if test_digests(source_file, dest_file):
                    print('OK.')
                    continue
                else:
                    print('Outdated')
                    os.remove(dest_file)
            else:
                print('Creating.')
            shutil.copy(source_file, dest_file)
    print('Done.')
