import requests

import sys
from os.path import isfile

if sys.version_info[0] > 2:
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode

__version__ = '0.2.1'
HOST, PORT = 'localhost', 50070


class WebHDFSError(Exception):
    pass


def jsonpath(path):
    def wrapper(fn):
        def wrapped(*args, **kw):
            resp = fn(*args, **kw)
            if not resp.ok:
                raise WebHDFSError(resp.reason)

            reply = resp.json()
            for key in path:
                reply = reply[key]
            return reply
        return wrapped
    return wrapper


octperm = '{0:03o}'.format
intparam = '{0:d}'.format
boolparam = {True: 'true', False: 'false'}.get


class WebHDFS(object):
    def __init__(self, host=HOST, port=PORT, **kw):
        self.host, self.port = host, port
        self.base_url = self._gen_base(self.host, self.port)
        self.user = kw.get('user')

    @jsonpath(['FileStatuses', 'FileStatus'])
    def listdir(self, path):
        return self._op('GET', path, 'LISTSTATUS')

    @jsonpath(['FileStatus'])
    def stat(self, path):
        return self._op('GET', path, 'GETFILESTATUS')

    @jsonpath(['FileChecksum'])
    def checksum(self, path, follow_redirects=False):
        resp = self._op('GET', path, 'GETFILECHECKSUM')
        url = self._get_redirect(resp, follow_redirects=follow_redirects)
        return requests.get(url)

    @jsonpath(['Path'])
    def home(self):
        return self._op('GET', '/', 'GETHOMEDIRECTORY')

    def chmod(self, mode, path):
        query = {'permission':  octperm(mode)}
        self._op('PUT', path, 'SETPERMISSION', query)

    def chown(self, path, user=None, group=None):
        query = {}
        if user:
            query['owner'] = user
        if group:
            query['group'] = group

        if not query:
            raise WebHDFSError('need to specify at least one of user or group')

        self._op('PUT', path, 'SETOWNER', query=query)

    def read(self, path, offset=0, length=0, buffersize=0, follow_redirects=False):
        # FIXME: Find a way to unite handling of optional parameters
        query = {}
        if offset:
            query['offset'] = intparam(offset)
        if length:
            query['length'] = intparam(length)
        if buffersize:
            query['buffersize'] = intparam(buffersize)

        resp = self._op('GET', path, 'OPEN', query=query)
        url = self._get_redirect(resp, follow_redirects=follow_redirects)
        return requests.get(url).content

    def put(self, local, path, overwrite=False, blocksize=0, replication=0,
            permission=0, buffersize=0):

        query = {'overwrite': boolparam(overwrite)}
        if blocksize:
            query['blocksize'] = intparam(blocksize)
        if replication:
            query['replication'] = intparam(replication)
        if permission:
            query['permission'] = octperm(permission)
        if buffersize:
            query['buffersize'] = intparam(buffersize)

        self._put('CREATE', 'PUT', local, path, query)

    def append(self, local, path, buffersize=0, follow_redirects=False):
        query = {}
        if buffersize:
            query['buffersize'] = intparam(buffersize)
        self._put('APPEND', 'POST', local, path, query, follow_redirects=follow_redirects)

    @jsonpath(['boolean'])
    def mkdir(self, path, permission=0):
        query = {}
        if permission:
            query = {'permission': octperm(permission)}

        return self._op('PUT', path, 'MKDIRS', query)

    @jsonpath(['boolean'])
    def rename(self, path, to):
        query = {'destination': to}
        return self._op('PUT', path, 'RENAME', query)

    @jsonpath(['boolean'])
    def delete(self, path, recursive=False):
        query = {'recursive': boolparam(recursive)}
        return self._op('DELETE', path, 'DELETE', query)


    # Below here are some utility functions
    def _put(self, op, method, local, path, query, follow_redirects=False):
        if not isfile(local):
            raise WebHDFSError('put error: {0} not found'.format(local))

        resp = self._op(method, path, op, query)
        url = self._get_redirect(resp, follow_redirects=follow_redirects)

        with open(local) as fo:
            data = fo.read()

        resp = requests.request(method, url, data=data)
        self._check_resp(resp)

    def _get_redirect(self, resp, follow_redirects=False):
        url = urlparse(resp.headers['Location'])
        if not follow_redirects:
            # The host in the redirect URL is *internal* one, so we need to fix
            # the url. Otherwise we'd just follow the redirects            
            host, port = url.netloc.split(':')
            url = url._replace(netloc='{0}:{1}'.format(self.host, port))
        return url.geturl()

    def _check_resp(self, resp):
        if not resp.ok:
            raise WebHDFSError(resp.reason)
        return resp

    def _op(self, method, path, op, query=None):
        url = '{0}{1}?op={2}'.format(self.base_url, path, op)

        if self.user:
            url += '&user.name={0}'.format(self.user)

        if query:
            url += '&{0}'.format(urlencode(query))

        resp = requests.request(method, url, allow_redirects=False)
        return self._check_resp(resp)

    def _gen_base(self, host, port):
        return 'http://{0}:{1}/webhdfs/v1'.format(host, port)
