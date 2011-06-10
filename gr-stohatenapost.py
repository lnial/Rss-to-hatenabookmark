#! /usr/bin/env python
# -*- coding:utf-8 -*-

from hashlib import sha1 as sha
import feedparser
import random
import datetime, time
import base64
import httplib

#e.g.)
#
#username = 'hatena user name'
#passwd = 'hatena password'
#hatenatag = '[googleReaderStar]'   <- add comment and tag
#atomfeed = 'http://~~.rss'   <- RSS  

username = ''
passwd = ''
hatenatag = '[googleReaderStar]'
atomfeed = ''


class AtomClient:
  def __init__(self):
    self.endopoint = None
    self.wsse = None

  def credentials(self, endpoint, user, password):
    nonce = sha(str(time.time() + random.random())).digest()
    now = datetime.datetime.now().isoformat() + "Z"
    digest = sha(nonce + now + password).digest()

    wsse = 'UsernameToken Username="%(u)s", PasswordDigest="%(p)s", Nonce="%(n)s", Created="%(c)s"'
    value = dict(u = user, p = base64.encodestring(digest).strip(),
           n = base64.encodestring(nonce).strip(), c = now)

    self.endpoint = endpoint
    self.wsse = wsse % value

  def atom_request(self, method, URI, body):
    con = httplib.HTTPConnection(self.endpoint)
    con.request(method, URI, body, {'X-WSSE' : self.wsse,'Content-Type':'text/xml','User-Agent': 'Python WSSE'})
    r = con.getresponse()

    response = dict(status=r.status, reason=r.reason, data=r.read())
    con.close()
    return response

class HateBu(AtomClient):
  def upload_entry(self, url, comment):
    entry = '''<entry xmlns="http://purl.org/atom/ns#">
                 <title>dummy</title>
                 <link rel="related" type="text/html" href="%s"/>
                 <summary type="text/plain">%s</summary>
               </entry>'''
    return self.atom_request('POST', '/atom/post', entry%(url, comment))


if __name__ == "__main__":

  #google star Atom
  atom = feedparser.parse(atomfeed)
  hp = HateBu()
  hp.credentials('b.hatena.ne.jp', username, passwd)
  for entry in atom['entries']:
    link = entry['link']
    hp.upload_entry(link, hatenatag)
  



