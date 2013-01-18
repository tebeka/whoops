import requests
import sys

if sys.version_info[0] > 2:
    from urllib.parse import urlparse, urlencode
else:
    from urlparse import urlparse
    from urllib import urlencode

HOST, PORT = 'localhost', 50070

class WebHDFSError(Exception):
    pass

class WebHDFS(object):
    def __init__(self, host=HOST, port=PORT, **kw):
        self.host, self.port = host, port
        self.base_url = self._gen_base(self.host, self.port)
        self.user = kw.get('user')

    def listdir(self, path):
        return self._op('GET', path, 'LISTSTATUS', ['FileStatuses', 'FileStatus'])

    def stat(self, path):
        return self._op('GET', path, 'GETFILESTATUS', ['FileStatus'])

    def checksum(self, path):
        return self._op('GET', path, 'GETFILECHECKSUM', ['FileChecksum'])

    def home(self):
        return self._op('GET', '/', 'GETHOMEDIRECTORY')

    def chmod(self, path, mode):
        return self._op('PUT', path, 'SETPERMISSION',
                        permission='{:o}'.format(mode))

    def _call(self, method, url):
        resp = requests.request(method, url, allow_redirects=False)
        while True:
            if not resp.ok:
                raise WebHDFSError(resp.reason)

            if resp.status_code != 307:
                return resp

            # The host in the redirect URL is *internal* one, so we need to fix the
            # url. Otherwise we'd just follow the redirects
            url = urlparse(resp.headers['Location'])
            host, port = url.netloc.split(':')
            url = url._replace(netloc='{}:{}'.format(self.host, port))

            resp = requests.request(
                method, url.geturl(), allow_redirects=False)

        return resp

    def _op(self, method, path, op, getters=None, **query):
        url = '{}{}?op={}'.format(self.base_url, path, op)

        if self.user:
            url += '&user.name={}'.format(self.user)

        if query:
            url += '&{}'.format(urlencode(query))

        resp = self._call(method, url)
        if not resp.ok:
            raise WebHDFSError


        reply = resp.json() if resp.content else {}
        for key in (getters or []):
            reply = reply[key]

        return reply

    def _find_host(self, url):
        url = urlparse(url)
        host = url.netloc
        i = host.find(':')
        return host if i == -1 else host[:i]

    def _gen_base(self, host, port):
        return 'http://{}:{}/webhdfs/v1'.format(host, port)

