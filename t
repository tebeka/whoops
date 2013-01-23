#!/usr/bin/env python


from webhdfs import WebHDFS

conn = WebHDFS('192.168.1.143', user='hdfs')
remote = '/tmp/z138'
new = '/tmp/8z'
print('put')
conn.put('README.rst', remote, overwrite=True)
print('listdir')
print(conn.listdir('/tmp'))
print('stat')
print(conn.stat(remote))
print('checksum')
print(conn.checksum(remote))
print('home')
print(conn.home())
print('chmod')
conn.chmod(0o777, remote)
print('chown')
conn.chown('cloudera', remote)
print('open')
print(conn.read(remote).decode('utf-8'))
print('append')
conn.append(__file__, remote)
print('mkdir')
print(conn.mkdir('/tmp/zolo'))
print('rename')
print(conn.rename(remote, new))
print('delete')
print(conn.delete(new))
