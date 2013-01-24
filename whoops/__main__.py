#!/usr/bin/env python

from whoops import WebHDFS, WebHDFSError, HOST, PORT, __version__
from requests import ConnectionError

from argparse import ArgumentParser
from fnmatch import fnmatch
from os import environ
from os.path import basename, dirname, isfile
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


def get(args):
    mode = 'ab' if args.append else 'wb'
    try:
        out = open(args.dest, mode)
    except IOError as err:
        raise WebHDFSError('cannot open {} - {}'.format(args.dest, err))

    try:
        data = fs.read(args.src, args.offset, args.length, args.buffersize)
        out.write(data)
    finally:
        out.close()


def put(args):
    if not isfile(args.src):
        raise WebHDFSError('{} is not a file'.format(args.src))

    fs.put(args.src, args.dest, args.overwrite, args.blocksize,
           args.replication, args.mode, args.buffersize)


def append(args):
    if not isfile(args.src):
        raise WebHDFSError('{} is not a file'.format(args.src))

    fs.append(args.src, args.dest, args.buffersize)


def mkdir(args):
    fs.mkdir(args.path, args.mode)


def mv(args):
    fs.rename(args.src, args.dest)


def rm(args):
    fs.delete(args.path, args.recursive)


def main(argv=None):
    global fs
    import sys

    argv = argv or sys.argv

    parser = ArgumentParser(description='webhdfs client')
    parser.add_argument('--host', help='webhdfs host', default=None)
    parser.add_argument('--port', help='webhdfs port', type=int,
                        default=None)
    parser.add_argument('--user', help='webhdfs user', default=None)
    parser.add_argument('--version', action='version',
                        version='whoops {}'.format(__version__))

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

    get_parser = subs.add_parser('get')
    get_parser.add_argument('src')
    get_parser.add_argument('dest')
    get_parser.add_argument('-o', '--offset', type=int, default=0)
    get_parser.add_argument('-l', '--length', type=int, default=0)
    get_parser.add_argument('-b', '--buffersize', type=int, default=0)
    get_parser.add_argument('-a', '--append', action='store_true',
                            default=False)
    get_parser.set_defaults(func=get)

    put_parser = subs.add_parser('put')
    put_parser.add_argument('src')
    put_parser.add_argument('dest')
    put_parser.add_argument('-o', '--overwrite', action='store_true',
                            default=False)
    put_parser.add_argument('-k', '--blocksize', type=int, default=0)
    put_parser.add_argument('-r', '--replication', type=int, default=0)
    put_parser.add_argument('-b', '--buffersize', type=int, default=0)
    put_parser.add_argument('-m', '--mode', type=lambda v: int(v, 8))
    put_parser.set_defaults(func=put)

    append_parser = subs.add_parser('append')
    append_parser.add_argument('src')
    append_parser.add_argument('dest')
    append_parser.add_argument('-b', '--buffersize', type=int, default=0)
    append_parser.set_defaults(func=append)

    mkdir_parser = subs.add_parser('mkdir')
    mkdir_parser.add_argument('path')
    mkdir_parser.add_argument('-m', '--mode', type=lambda v: int(v, 8))
    mkdir_parser.set_defaults(func=mkdir)

    mv_parser = subs.add_parser('mv')
    mv_parser.add_argument('src')
    mv_parser.add_argument('dest')
    mv_parser.set_defaults(func=mv)

    rm_parser = subs.add_parser('rm')
    rm_parser.add_argument('path')
    rm_parser.add_argument('-r', '--recursive', action='store_true',
                           default=False)
    rm_parser.set_defaults(func=rm)

    args = parser.parse_args(argv[1:])

    host = args.host or environ.get('WEBHDFS_HOST') or HOST
    port = args.port or environ.get('WEBHDFS_PORT') or PORT
    user = args.user or environ.get('WEBHDFS_USER') or None

    fs = WebHDFS(host, port, user=user)

    try:
        args.func(args)
    except WebHDFSError as err:
        raise SystemExit('error: {}'.format(err))
    except ConnectionError as err:
        raise SystemExit(
            'error: cannot connect - {}'.format(err.args[0].reason))


if __name__ == '__main__':
    main()
