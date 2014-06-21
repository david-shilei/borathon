from urllib2 import urlopen
import re, os, tarfile, zipfile
from bs4 import BeautifulSoup  

# config
URL_PREFIX="http://engweb.eng.vmware.com/bugs/files/0/"
LOCAL_DIR="/tmp/"


# foler_path: like http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/
# return array of urls for tgz files

def getTgzFiles(folder_path):
    page = BeautifulSoup(urlopen(url).read())
    urls = []
    for link in page.findAll('a', href=re.compile(r'.*\.tgz')):
        urls.append(folder_path + '/' + link['href'])
    return urls 


# url must be fully extended address ending with ".tgz"
def downloadFile(url):
    req = urlopen(url)
    filename = os.path.basename(url)
    print filename
    local_path = LOCAL_DIR + filename
    if(os.path.exists(local_path)):
        print("%s already exists, won't download again" % local_path)
        return local_path

    CHUNK = 16*1024
    with open(local_path, 'wb') as f:
        while True:
            chunk = req.read(CHUNK)
            if not chunk: break
            f.write(chunk)
        f.flush()
        f.close()
    return local_path

def downloadFiles(urls):
    local_paths = []
    for url in urls:
        local_paths.append(downloadFile(url))
    return local_paths

def extractFile(path, to_directory):
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

def extractFiles(paths, to_dir=LOCAL_DIR):
    for path in paths:
        print "extracting file %s" % path
        extractFile(path, to_dir)
    
def processUrl(url):
    pattern = r"(?P<number>\d{7})(?P<subpath>(/.*)*)/\*\.tgz"
    p = re.compile(pattern)
    m = p.match(url)
    if m:
        folder_path = URL_PREFIX + '/'.join(list(m.group('number'))) + m.group('subpath')
        urls = getTgzFiles(folder_path)
        return urls
    return []

def validateTgzUrl(url):
    return url.startsWith("http") and url.endsWith('.tgz')
    
if __name__ == '__main__':
    url = "http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/"
    urls = getTgzFiles(url)
    local_paths = downloadFiles(urls)
    extractFiles(local_paths)
