#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import getpass
import socket

def println(s, file=sys.stderr):
    assert type(s) is type(u'')
    file.write(s.encode(sys.getfilesystemencoding(), 'replace') + os.linesep)

try:
    socket.create_connection(('127.0.0.1', 8087), timeout=1).close()
    os.environ['HTTPS_PROXY'] = '127.0.0.1:8087'
except socket.error:
    println(u'警告：建议先启动 goagent 客户端或者 VPN 然后再上传，如果您的 VPN 已经打开的话，请按回车键继续。')
    if not os.getenv('USE_DOCKER'):
        raw_input()

sys.modules.pop('google', None)
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../google_appengine.zip')))

import mimetypes
mimetypes._winreg = None

import urllib2
import fancy_urllib
fancy_urllib.FancyHTTPSHandler = urllib2.HTTPSHandler

_realgetpass = getpass.getpass
def getpass_getpass(prompt='Password:', stream=None):
    if os.getenv('USE_DOCKER'):
        return os.getenv('GAE_PASSWORD')
    try:
        import msvcrt
    except ImportError:
        return _realgetpass(prompt, stream)
    password = ''
    sys.stdout.write(prompt)
    while True:
        ch = msvcrt.getch()
        if ch == '\b':
            if password:
                password = password[:-1]
                sys.stdout.write('\b \b')
            else:
                continue
        elif ch == '\r':
            sys.stdout.write(os.linesep)
            return password
        else:
            password += ch
            sys.stdout.write('*')
getpass.getpass = getpass_getpass


from google.appengine.tools import appengine_rpc, appcfg
appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH = './.appcfg_cookies'

def upload(dirname, appid):
    assert isinstance(dirname, basestring) and isinstance(appid, basestring)
    filename = os.path.join(dirname, 'app.yaml')
    template_filename = os.path.join(dirname, 'app.template.yaml')
    assert os.path.isfile(template_filename), u'%s not exists!' % template_filename
    with open(template_filename, 'rb') as fp:
        yaml = fp.read()
    with open(filename, 'wb') as fp:
        fp.write(re.sub(r'application:\s*\S+', 'application: '+appid, yaml))

    if os.getenv('USE_DOCKER'):
        auth_argv = ['appcfg', '--email=' + os.getenv('GAE_EMAIL')]
        rollback_argv = auth_argv + ['rollback', dirname]
        upload_argv = auth_argv + ['update', dirname]
    else:
        rollback_argv = ['appcfg', 'rollback', dirname]
        upload_argv = ['appcfg', 'update', dirname]

    try:
        appcfg.main(rollback_argv)
    except AttributeError:
        println(u'错误的 password，请确认是否输入正确')
        sys.exit(-1)
    appcfg.main(upload_argv)


def get_appids():
    if not os.getenv('USE_DOCKER'):
        appids = raw_input('APPID:')
    else:
        appids = os.getenv('GAE_APPIDS')
    if not re.match(r'[0-9a-zA-Z\-|]+', appids):
        println(u'错误的 appid 格式，请登录 http://appengine.google.com 查看您的 appid!')
        sys.exit(-1)
    if any(x in appids.lower() for x in ('ios', 'android', 'mobile')):
        println(u'appid 不能包含 ios/android/mobile 等字样。')
        sys.exit(-1)
    return appids.split('|')


def main():
    appids = get_appids()
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    try:
        os.remove(appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH)
    except OSError:
        pass
    for appid in appids:
        upload('gae', appid)
    try:
        os.remove(appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH)
    except OSError:
        pass


if __name__ == '__main__':
    println(u'''\
===============================================================
 GoAgent服务端部署程序, 开始上传 gae 应用文件夹
 Linux/Mac 用户, 请使用 python uploader.py 来上传应用
===============================================================

请输入您的appid, 多个appid请用|号隔开
注意：appid 请勿包含 ios/android/mobile 等字样，否则可能被某些网站识别成移动设备。
        '''.strip())
    main()
    println(os.linesep + u'上传成功，请不要忘记编辑proxy.ini把你的appid填进去，谢谢。按回车键退出程序。')
    if not os.getenv('USE_DOCKER'):
        raw_input()
