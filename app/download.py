from urllib2 import urlopen
import re
from bs4 import BeautifulSoup  

#test config
url="http://engweb.eng.vmware.com/bugs/files/0/1/2/6/3/8/3/2/"
localdir="/tmp/"

def getTgzFiles(url):
	page = BeautifulSoup(urlopen(url).read())
	files = []
	for link in page.findAll('a', href=re.compile(r'.*\.tgz')):
		files.append(link['href'])
	return files


def downloadFile(url, filename):
	req = urlopen(url + filename)
	local_filename = localdir + filename
	CHUNK = 16*1024
	with open(local_filename, 'wb') as f:
		for chunk in req.read(CHUNK):
			if chunk:
				f.write(chunk)
				f.flush()
		localfile.close()
		return local_filename

def downloadFiles(url, filelist):
	for filename in filelist:
		downloadFile(url, filename)

if __name__ == '__main__':
	files = getTgzFiles(url)
	downloadFiles(url, files)
