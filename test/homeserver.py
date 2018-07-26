#! /usr/bin/env python
# -*- coding:utf8 -*-

import sys, logging, threading, os, socket, select
import paramiko
from scp import SCPClient
from logging.handlers import RotatingFileHandler
import tarfile, bz2
import shutil, time
import sqlite3
import re, datetime
import traceback

FORMAT = '[%(asctime)-15s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s'
formatter = logging.Formatter(FORMAT)
loghandler = RotatingFileHandler('homeserver.log', 'a', 10*1024*1024, 10)
loghandler.setFormatter(formatter)

logger = logging.getLogger('mc2')
logger.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

class TextCtlLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        FORMAT = '[%(asctime)-15s] %(levelname)s %(message)s\r\n'
        formatter = logging.Formatter(FORMAT)
        self.setFormatter(formatter)
        
    def emit(self, record):
        print(self.format(record))

logger.addHandler(TextCtlLogHandler())

class R():
    devices = [
        #['08:08:08:08:08:08', '192.168.1.10', 'ADT-10', '1.1.135'],
    ]

    macs = [
        #['08:08:08:08:08:08', 1],
    ]

id_rsa = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA0K8mVbEcIE3/y25v7sadX9LaMOfVM5F1cEC3v022gVbye8TR
m0eIj7ApRZq41eJLmgqAE+DdFVL13JZG/Jhe+oRY9SOm6cTXG955BiME/8DymA6B
4a46d1UnLoVzQbkZHdNqxsUlqxqHpcZxRu5Jgoz/BxYl6CmGfiPKishAtCnL4aTa
gr+DWIcY0WMBWL1hHyR1PDLibIkV2GZniyE3E2bRUM0DTFESdqorOhhMBheuk6l7
e2ZXHvvrH2p5yQkxWUQy4LvrL9UFzJUbaigXUX809EQL+U3xo4VTzOZtWceKn7R/
dJ/tIoeJdp8nZUD02RZAPYrIyIhgXX/B4K2QlwIDAQABAoIBABtjMTvDz7Yppm1z
Y/tJU7QUvw/2DRQEfg4qYDMaJt6Yo6A8t2mSnMiGzRPWd3WSimt//0kclMdMqPm3
Oz/BW42zOt2JPUmmzLhanTWB+RD7qJruJHuS2xd4NHk1iGfSvAofCf9mNkhbZfwK
rCkr8rfQe1PZw0XR1VXOqrFGEL/UE4oQhctuJf+6X98nrBCseIHXTSdb/rABaWD2
erQG2Q3J/TnH7ndOSaDmW31WzxWuNJXI7Qb/g3ek/zCB1dcZD/aoaDxmPMpr/gSb
v45ikryFXZRCifQpQAkaA2x47pfqAa3wWQQh+8FIkWgP/kdTWWhRJRmG4/8USGr+
MGvfuUECgYEA++yrZBoK1vVMSKTPoaA9JPo4VAXTldW1/pb1J4SeUdDosruu3QNm
hoT1m6BEuFDonW9vRe0LfWPNMmVPS17rrTJXjbnXE2wKidZCNF1rYFI/89gmIL7t
03raYLuqAHwJjuprYTXjtBOv09uAHTiD5C4ee6Yb2Kig61N8eyz7rncCgYEA1A9n
LUAjnuiAcWtryADe9+LaH2gpuP1UKnE3wYsQTUQRoRq5PgeINVrr4W5ct3/O838z
Xnva+HkA3DhsfHUpH1HsHM8TejJuHQ6HZru3PBGq/zk498wfpKbdl5aRbeH7AvFC
XPGHCbmtoeIn7dR4Op1/glEhkNncdaBNhmUdFuECgYEA8RGrfHGzN7mpksYrbdWB
TTYn2rdsni/QJNxdocA1I8OOOSKCFTogzM7EnHSD7gB2Z9jvmPFZklaDUBtEArLF
QYov4A4asporh3TBC4ztqFFsozGOYr1xpXIlMHXEGwyWtOy7bl18FKDWGxwrf0rK
YvqC7v2oHe5XdnkAYHpOKMcCgYEAihqx7jVcPWxb4gG8gteWXkfeGCAlM/W/r5hm
YGSprDhNZudZhr0vBth80CaouVTCObA4iysMU0+ysLkKZg+DRYN7ytNNcwKO1duV
cOGFlthGzcq9gBvu67NEkyma8r3+VE89Efy2Hi5PlyMLMAd0eXADD6K4wnYv7mcE
tib5x+ECgYEAyv8C2hU5lhC+2WIrrXZLgLkuhSa/uD5BgYNX9bumwABi6rNbTVTm
n44IWtionCEYHbpj729t0OMhMEUMmVD78waGqHktkfyLmQS7Hlsfun98FEvs0xNz
zpErZDbtSaqvbk6UCi3zG8TVr3sTmdIaPl/LfKGHQQrWWuZfWV2m9K0=
-----END RSA PRIVATE KEY-----'''

class FileObject():
    def __init__(self, data=''):
        self.data = data
    
    def __len__(self):
        return len(self.data)
        
    def readlines(self):
        return self.data.split('\n')

class Clone(threading.Thread):
    def __init__(self, src=None, dst=None):
        if not src or not dst:
            raise Exception('no src or dst')
        self.src = (src, 22)
        self.dst = (dst, 22)
        threading.Thread.__init__(self)

    def progress(self, path, size, offset):
        label = int((offset*1.0/size*100))
        if 0 == label % 20:
            logger.info('%s %d%s', path, int((offset*1.0/size*100)), '%')

    def run(self):
        path = 'PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin;'
        pkey = paramiko.rsakey.RSAKey.from_private_key(FileObject(id_rsa))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.src[0], port=self.src[1], username='root', pkey=pkey, timeout=5)
        scp = SCPClient(ssh.get_transport(), progress=self.progress)
        logger.info('Connect %s', self.src[0])
        stdin, stdout, stderr = ssh.exec_command(path+'cat /etc/VERSION;')
        version = stdout.read().decode()
        logger.info('VERSION %s', version)
        os.system('rm -rf rootfs')
        os.system('mkdir -p rootfs/var/lib/asterisk')
        os.system('mkdir -p rootfs/var/www/html')
        os.system('mkdir -p rootfs/var/log/asterisk/voicemail')
        scp.get('/var/lib/asterisk/moh', 'rootfs/var/lib/asterisk/')
        scp.get('/var/www/html/avatar', 'rootfs/var/www/html/')
        scp.get('/var/log/asterisk/voicemail/default', 'rootfs/var/log/asterisk/voicemail/')
        scp.get('/var/log/asterisk/master.db', 'rootfs/var/log/asterisk/master.db')
        scp.get('/var/lib/asterisk/realtime.sqlite3', 'rootfs/var/lib/asterisk/realtime.sqlite3')
        stdin, stdout, stderr = ssh.exec_command(path+'ls -l /etc/localtime;')
        localtime = stdout.read().decode()
        pattern = re.compile('.*\/etc\/localtime -> \/usr\/share\/zoneinfo\/Etc\/GMT([+-]\d+)')
        match = pattern.match(localtime)
        gmt = 'GMT+8'
        if match:
            gmt = 'GMT' + match.group(1)
        logger.info('localtime %s', gmt)
        ssh.close()
        ssh.connect(hostname=self.dst[0], port=self.dst[1], username='root', pkey=pkey, timeout=5)
        scp = SCPClient(ssh.get_transport(), progress=self.progress)
        logger.info('Connect %s', self.src[0])
        stdin, stdout, stderr = ssh.exec_command(path+'cat /etc/VERSION;')
        version = stdout.read().decode()
        logger.info('VERSION %s', version)
        stdin, stdout, stderr = ssh.exec_command(path+'/etc/init.d/monitor stop')
        logger.info('STOP MONITOR %s', stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command(path+'/etc/init.d/nginx stop')
        logger.info('STOP NGINX %s', stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command(path+'/etc/init.d/php-fpm stop')
        logger.info('STOP PHP-FPM %s', stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command(path+'/etc/init.d/asterisk stop')
        logger.info('STOP ASTERISK %s', stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command(path+'/etc/init.d/led stop')
        logger.info('STOP LED %s', stdout.read().decode())

        scp.put('rootfs/var/lib/asterisk/moh', '/var/lib/asterisk/')
        scp.put('rootfs/var/www/html/avatar', '/var/www/html/')
        scp.put('rootfs/var/log/asterisk/voicemail/default', '/var/log/asterisk/voicemail/')
        scp.put('rootfs/var/log/asterisk/master.db', '/var/log/asterisk/master.db')
        scp.put('rootfs/var/lib/asterisk/realtime.sqlite3', '/var/lib/asterisk/realtime.sqlite3')
        stdin, stdout, stderr = ssh.exec_command(path+'ln -sf /usr/share/zoneinfo/Etc/' +gmt+ ' /etc/localtime;ls -l /etc/localtime;')
        localtime = stdout.read().decode()
        match = pattern.match(localtime)
        if match:
            gmt = 'GMT' + match.group(1)
        logger.info('localtime %s', gmt)
        stdin, stdout, stderr = ssh.exec_command(path+('sync;'*10))
        logger.info('SYNC %s', stdout.read().decode())
        stdin, stdout, stderr = ssh.exec_command(path+'reboot')
        logger.info('REBOOT %s', stdout.read().decode())
        ssh.close()
        return 0

def main(argv):
    c = Clone(src=argv[1], dst=argv[2])
    c.run()
    return 0
            
if __name__ == "__main__":
    main(sys.argv)
