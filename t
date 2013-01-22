#!/usr/bin/env python


from webhdfs import WebHDFS

conn = WebHDFS('192.168.1.121', user='hdfs')
remote = '/tmp/z138'
# print('listdir')
# print(conn.listdir('/tmp'))
# print('stat')
# print(conn.stat(remote))
# print('checksum')
# print(conn.checksum(remote))
# print('home')
# print(conn.home())
# print('chmod')
# conn.chmod(remote, 0o777)
# print('chown')
# conn.chown(remote, 'cloudera')
# print('open')
# print(conn.read(remote).decode('utf-8'))
# print('put')
# conn.put('README.rst', remote, overwrite=True)
# print('append')
# conn.append(__file__, remote)
# print('mkdir')
# print(conn.mkdir('/tmp/zolo'))
print('rename')
print(conn.rename(remote, '/tmp/8z'))
