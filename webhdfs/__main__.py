#!/usr/bin/env python

from webhdfs import WebHDFS, WebHDFSError
from requests import ConnectionError

from argparse import ArgumentParser
from fnmatch import fnmatch
from os.path import basename, dirname
from time import localtime, strftime
import re

fs = None

def stat_long(stat, path):
    time = stat['modificationTime']/1000
    stat['mod'] = strftime('%b %d %H:%M', localtime(time))
    stat['path'] = stat['pathSuffix'] or path
    fmt = '{permission:4} {length:10} {owner:8} {group:10} {mod} {path}'
    return fmt.format(**stat)

def stat_short(stat, path):
    return stat['pathSuffix'] or path


def ls(args):
    base = basename(args.path)
    if re.search('[?*\[\]]', base):
        path = dirname(args.path)
        is_glob = True
    else:
        path = args.path
        is_glob = False

    fmt = stat_long if args.long else stat_short
    for stat in fs.listdir(path):
        if is_glob and not fnmatch(stat['pathSuffix'] or path, base):
            continue
        print(fmt(stat, args.path))

def stat(args):
    info = fs.stat(args.path)
    msize = max(len(key) for key in info)
    fmt = '{{:{}}}: {{}}'.format(msize)
    for key, value in info.items():
        print(fmt.format(key, value))

def checksum(args):
    print(fs.checksum(args.path)['bytes'])

def home(args):
    print(fs.home())

def chmod(args):
    fs.chmod(args.mode, args.path)

def chown(args):
    if not (args.user or args.group):
        raise WebHDFSError('need either user or group')
    fs.chown(args.path, args.user, args.group)

def main(argv=None):
    global fs
    import sys

    argv = argv or sys.argv

    parser = ArgumentParser(description='webhdfs client')
    parser.add_argument('--host', help='webhdfs host', default='localhost')
    parser.add_argument('--port', help='webhdfs port', type=int,
                        default='50070')
    parser.add_argument('--user', help='webhdfs user', default=None)

    subs = parser.add_subparsers()

    ls_parser = subs.add_parser('ls')
    ls_parser.add_argument('path')
    ls_parser.add_argument('-l', help='long format', default=False,
                           action='store_true', dest='long')
    ls_parser.set_defaults(func=ls)

    stat_parser = subs.add_parser('stat')
    stat_parser.add_argument('path')
    stat_parser.set_defaults(func=stat)

    cs_parser = subs.add_parser('checksum')
    cs_parser.add_argument('path')
    cs_parser.set_defaults(func=checksum)

    home_parser = subs.add_parser('home')
    home_parser.set_defaults(func=home)

    chmod_parser = subs.add_parser('chmod')
    chmod_parser.add_argument('mode', type=lambda v: int(v, 8))
    chmod_parser.add_argument('path')
    chmod_parser.set_defaults(func=chmod)

    chown_parser = subs.add_parser('chown')
    chown_parser.add_argument('path')
    chown_parser.add_argument('-u', '--user', help='user')
    chown_parser.add_argument('-g', '--group', help='group')
    chown_parser.set_defaults(func=chown)


    args = parser.parse_args(argv[1:])

    fs = WebHDFS(args.host, args.port, user=args.user)

    try:
        args.func(args)
    except WebHDFSError as err:
        raise SystemExit('error: {}'.format(err))
    except ConnectionError as err:
        raise SystemExit('error: cannot connect - {}'.format(err.args[0].reason))


if __name__ == '__main__':
    main()

