#!/usr/bin/env python

from webhdfs import WebHDFS, WebHDFSError
from argparse import ArgumentParser
from time import localtime, strftime

fs = None

def stat_long(stat):
    time = stat['modificationTime']/1000
    stat['mod'] = strftime('%b %d %H:%M', localtime(time))
    fmt = '{permission:4} {length:10} {owner:8} {group:10} {mod} {pathSuffix}'
    return fmt.format(**stat)

def stat_short(stat):
    return stat['pathSuffix']


def ls(args):
    fmt = stat_long if args.long else stat_short
    for stat in fs.listdir(args.path):
        print(fmt(stat))

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
    args = parser.parse_args(argv[1:])

    fs = WebHDFS(args.host, args.port, user=args.user)

    try:
        args.func(args)
    except WebHDFSError as err:
        raise SystemExit('error: {}'.format(err))


if __name__ == '__main__':
    main()

