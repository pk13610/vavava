#!/usr/bin/env python
# coding=utf-8

import urllib
import urllib2
import socket
from cookielib import LWPCookieJar
from io import BytesIO

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ' \
                     'en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
DEFAULT_REFERER = "http://www.google.com/"
DEFAULT_BUFFER_SIZE = 1024*1024
DEFAULT_CHARSET = "utf8"
DEFAULT_TIMEOUT = 30 #MS
DEFAULT_DEBUG_LVL = 0

class HttpUtil(object):
    """ a simple client of http"""
    def __init__(self,
                 charset=DEFAULT_CHARSET,
                 cookie=LWPCookieJar(),
                 timeout=DEFAULT_TIMEOUT,
                 debug_lvl=DEFAULT_DEBUG_LVL,
                 proxy=None,
                 log=None):
        self._cookie = cookie
        self._timeout = timeout
        self._proxy = proxy
        self._opener = None
        self._buffer_size = DEFAULT_BUFFER_SIZE
        self._charset = DEFAULT_CHARSET
        self._set_debug_level(debug_lvl)
        self._headers = {}
        self._headers['Referer'] = DEFAULT_REFERER
        self._headers['User-Agent'] = DEFAULT_USER_AGENT

    def get(self, url):
        self._init(force=True)
        return self._request(url).read(self._buffer_size)

    def post(self, url, post_dic):
        self._init(force=True)
        return self._request(
            url,
            post_data=urllib.urlencode(post_dic).encode(self._charset)
        ).read(self._buffer_size)

    def fetch(self, url, handler, post_data=None):
        if handler is None:
            raise ValueError, "need handler"
        self._init(force=True)
        handler.handle(req=None, resp=self._request(url, post_data))

    def add_header(self, key, value):
        self._headers[key] = value

    def _set_debug_level(self, level=0):
        from httplib import HTTPConnection
        HTTPConnection.debuglevel = level
        self._debug_lvl = level

    def _request(self, url, post_data=None):
        socket.setdefaulttimeout(self._timeout)
        req = urllib2.Request(url, data=post_data, headers=self._headers)
        return self._opener.open(req)

    def _init(self, force=False):
        #if self.handler and hasattr(self.handler, 'start'):
        #    self._headers['Content-Range'] = 'bytes %s-%s/%s' % (handler.start, handler.end, handler.len)
        #    self._headers['Content-Length'] = str(handler.len - handler.start)
        if self._opener is None:
            self._opener = urllib2.build_opener(ContentEncodingProcessor())
        if self._cookie:
            self._headers['Set-Cookie'] = self._cookie.as_lwp_str()
            self._opener.add_handler(urllib2.HTTPCookieProcessor(self._cookie))
        if self._proxy:
            self._opener.add_handler(urllib2.ProxyHandler(self._proxy))
        urllib2.install_opener(self._opener)

import time
import threading
class DownloadStreamHandler:
    """ download a http stream
          can not do this work by urllib2.BaseHandler way,
          I don't know how to stop download in tht middle of processing,
          other handler maybe cause a timeout I guess.
          so this handler works outside of urllib2.open()
    """
    def __init__(self, fp, duration=0, size=1400):
        self.buff_size = size
        self.fp = fp
        self.duration = duration
        self.ev = threading.Event()
        if duration > 0:
            self.stop_time = duration + time.time()

    def syn_stop(self):
        self.ev.set()

    def handle(self, req, resp):
        self.ev.clear()
        while not self.ev.is_set() \
            and self._handle(resp.read(self.buff_size)):
            pass

    def _handle(self, data):
        if not data: return False
        self.fp.write(data)
        return self.duration <= 0 or self.stop_time > time.time()

import gzip
import zlib
class ContentEncodingProcessor(urllib2.BaseHandler):
    """A handler to add gzip capabilities to urllib2 requests """
    # add headers to requests

    def __init__(self):
        try:
            self.deflate = lambda data: zlib.decompress(data, -1*zlib.MAX_WBITS)
        except zlib.error:
            self.deflate = lambda data: zlib.decompress(data)

    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip,deflate")
        return req

    def http_response(self, req, resp):
        old_resp = resp
        if resp.headers.get("content-encoding") == "gzip":
            gz = gzip.GzipFile( fileobj=BytesIO(resp.read()), mode="r" )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
            # deflate
        if resp.headers.get("content-encoding") == "deflate":
            gz = BytesIO( self.deflate(resp.read()) )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        return resp

import unittest
class TestMethod(unittest.TestCase):
    def test_get(self):
        url = r'http://www.twitter.com'
        client = HttpUtil()
        content=client.get(url)
        print(content.decode('utf8'))

    def test_post(self):
        url = r'http://www.2kdy.com/search.asp'
        post = {'searchword': r'lie'}
        client = HttpUtil(charset='gb2312')
        content=client.post(url, post)
        print content

    def test_fetch(self):
        url = r'http://pb.hd.sohu.com.cn/stats.gif?msg=caltime&vid=772959&tvid=596204&ua=pp&isHD=21&pid=348552429&uid=13832983422211404270&out=0&playListId=5029335&nid=353924663&tc=2400&type=vrs&cateid=&userid=&uuid=779b9c99-3c3a-52bc-2622-8bb0218cad5d&isp2p=0&catcode=101&systype=0&act=&st=144792%3B6560%3B143697%3B143699&ar=10&ye=2010&ag=5%u5C81%u4EE5%u4E0B&lb=2&xuid=&passport=&fver=201311211515&url=http%3A//tv.sohu.com/20120925/n353924663.shtml&lf=http%253A%252F%252Fv.baidu.com%252Fv%253Fword%253D%2525CA%2525AE%2525D2%2525BB%2525C2%2525DE%2525BA%2525BA%2526ct%253D301989888%2526rn%253D20%2526pn%253D0%2526db%253D0%2526s%253D0%2526fbl%253D800&autoplay=1&refer=http%3A//tv.sohu.com/20120925/n353924666.shtml&t=0.24127451563254'
        client = HttpUtil()
        #client.set_proxy({"http":"http://127.0.0.1:8087"})
        handle = DownloadStreamHandler(open('/Users/pk/Downloads/tmp.flv', 'w'), duration=10)
        client.fetch(url, handle)

if __name__ == '__main__':
    try:
        unittest.main()
    except(KeyboardInterrupt):
        print 'ctl+c'
