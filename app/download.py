from urllib2 import urlopen
import re
import os.path
import tarfile
import os
import zipfile
from bs4 import BeautifulSoup  

#test config
url="http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/"
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

	if(os.path.exists(local_filename)):
		print "%s already exists, does not download again" % local_filename

	CHUNK = 16*1024
	with open(local_filename, 'wb') as f:
		while True:
			chunk = req.read(CHUNK)
			if not chunk: break
			f.write(chunk)
		f.flush()
		f.close()
		return local_filename

def downloadFiles(url, filelist):
	for filename in filelist:
		downloadFile(url, filename)

def extractFile(path, to_directory='.'):
    if path.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif path.endswith('.tar.gz') or path.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif path.endswith('.tar.bz2') or path.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    else: 
        raise ValueError, "Could not extract `%s` as no appropriate extractor is found" % path
    
    cwd = os.getcwd()
    os.chdir(to_directory)
    
    try:
        file = opener(path, mode)
        try: file.extractall()
        finally: file.close()
    finally:
        os.chdir(cwd)

def extractFiles(files, to_dir):
	for file in files:
		extractFile(localdir + file, to_dir)

if __name__ == '__main__':
	files = getTgzFiles(url)
	downloadFiles(url, files)
	extractFiles(files, localdir)
