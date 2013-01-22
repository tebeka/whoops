#!/usr/bin/env python


from webhdfs import WebHDFS

conn = WebHDFS('192.168.1.121', user='hdfs')
# print('listdir')
# print(conn.listdir('/tmp'))
# print('stat')
# print(conn.stat('/tmp/z8'))
# print('checksum')
# print(conn.checksum('/tmp/z8'))
# print('home')
# print(conn.home())
# print('chmod')
# conn.chmod('/tmp/z8', 0o777)
# print('chown')
# conn.chown('/tmp/z8', 'cloudera')
# print('open')
# print(conn.read('/tmp/z8').decode('utf-8'))
# remote = '/tmp/z138'
# print('put')
# conn.put('README.rst', remote, overwrite=True)
# print('append')
# conn.append(__file__, remote)
print('mkdir')
print(conn.mkdir('/tmp/zolo'))
