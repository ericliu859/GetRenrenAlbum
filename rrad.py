import sys
import os
import re

import urllib
import urllib2
import cookielib

import cmd
import json
import getpass

class rrad():
	def __init__(self):
		self.download_dir = 'albums'
		if not os.path.isdir(self.download_dir):
			os.mkdir(self.download_dir)
		
		self.session = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
	
	def signin(self):
		username = raw_input('username:')
		password = getpass.getpass('password:')
		data = (
			('email',username),
			('password',password),
			('origURL',"http://www.renren.com/Home.do"),
			('domain',"renren.com")
		)
		page = self.session.open('http://www.renren.com/PLogin.do',urllib.urlencode(data))
		page.close()
	
	def signout(self):
		self.session.open('http://www.renren.com/Logout.do')
	
	def do_post(self,url):
		return self.session.open(url,{}).read()
	
	def do_get(self,url):
		return self.session.open(url).read()
	
	def get_album_info(self,album_url):
		photo_links = []
		album_name = album_url.split('/')[-1]
		content = self.do_get(album_url)
		links = re.findall(r'<a.*href="(.*)" class="picture">',content)
		if links:
			photo_links.extend([re.sub(r'\?.*$','',link) for link in links])
		return {'album_name': album_name,'photos':photo_links}
	def get_photo_file(self,photo_url):
		content = self.do_get(photo_url+'?psource=3&fromVIP=false')
		open('/Users/apple/Desktop/getPhoto/f.html','w').write(content)
		match = re.search(r'<img id="photo"(.*?) src="(?P<src>.*?)" ',content,flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
		return match and match.group('src')
	
	def save_photo_file(self,album_dir,photo_file):
		try:
			filename = photo_file.split('/')[-1]
			f = open(os.path.join(album_dir,filename),'wb')
			f.write(self.session.open(photo_file).read())
			f.close()
			return True
		except Exception, e:
			return False
	
	def save_album(self,url):
		album_url = re.sub(r'[\?\#].*$','',url)
		album_info= self.get_album_info(album_url)
		album_dir = os.path.join(self.download_dir,album_info['album_name'])
		if not os.path.isdir(album_dir): os.mkdir(album_dir)
	
		print 'saving album to',album_dir
		for i,link in enumerate(album_info['photos']):
			print '(%d/%d) %s' % (i+1,len(album_info['photos']),link),
			try:
				photo_file = self.get_photo_file(link)
				self.save_photo_file(album_dir,photo_file)
				print 'saved.'
			except:
				print 'failed.'
		print 'all downloads completed.'


class rradCmd(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = '> '
		self.rrad = rrad()
	
	def help_signin(self):
		print 'Sign into renren.com signin username password'
	def do_signin(self,null):
		self.rrad.signin()
	def help_save(self):
		print 'Save the given album. Example:save http://photo.renren.com/photo/320289729/album-517394069'
	def do_save(self,album_url):
		self.rrad.save_album(album_url)
	def help_exit(self):
		print 'Quit the application.'
	def do_exit(self,null):
		sys.exit(0)

if __name__ == '__main__':
	rrad_cmd = rradCmd()	#初始化rradCmd
	rrad_cmd.cmdloop()	#rrad_cmd循环
	
