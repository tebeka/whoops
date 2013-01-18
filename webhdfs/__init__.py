import requests

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '50070'

class WebHDFSError(Exception):
    pass

class WebHDFS(object):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host, self.port = host, port

    def listdir(self, path):
        url = 'http://{}:{}/webhdfs/v1{}?op=LISTSTATUS'.format(
            self.host, self.port, path)

        resp = requests.get(url)
        if not resp.ok:
            raise WebHDFSError

        return resp.json()['FileStatuses']['FileStatus']



