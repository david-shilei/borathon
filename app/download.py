import re, os, tarfile, zipfile, hashlib
from urllib2 import urlopen
from bs4 import BeautifulSoup
from mylogger import logger

# config
URL_PREFIX="http://engweb.eng.vmware.com/bugs/files/0/"
LOCAL_DIR="data"


# foler_path: like http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/
# return array of urls for tgz files

def getTgzFiles(folder_path):
    page = BeautifulSoup(urlopen(folder_path).read())
    urls = []
    for link in page.findAll('a', href=re.compile(r'.*\.tgz')):
        urls.append(folder_path + '/' + link['href'])
    return urls


# url must be fully extended address ending with ".tgz"
def downloadFile(local_new_dir, url):
    filename = os.path.basename(url)
    logger.debug("Downloading " + filename)
    local_path = os.path.join(local_new_dir, filename)
    if(os.path.exists(local_path)):
        logger.debug("%s already exists, won't download again" % local_path)
        return local_path

    req = urlopen(url)
    CHUNK = 16*1024
    with open(local_path, 'wb') as f:
        while True:
            chunk = req.read(CHUNK)
            if not chunk: break
            f.write(chunk)
        f.flush()
        f.close()
    return local_path

def downloadFiles(newdir, urls):
    local_new_dir = os.path.join(LOCAL_DIR, newdir)
    if not os.path.isdir(local_new_dir):
        print ">>>create new directory %s" % local_new_dir
        os.makedirs(local_new_dir)
    local_paths = []
    for url in urls:
        local_paths.append(downloadFile(local_new_dir, url))
    return local_paths

# extract tgz file to the directory
def extractFile(path, to_directory=None):
    if path.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif path.endswith('.tar.gz') or path.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif path.endswith('.tar.bz2') or path.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    else:
        raise ValueError, "Could not extract `%s` as no appropriate extractor is found" % path

    cwd = os.getcwd()
    if to_directory is None:
        to_directory = os.path.dirname(cwd + '/' +  path)
        print to_directory
    os.chdir(to_directory)

    try:
        file = opener(cwd + '/' + path , mode)
        file.extractall()
        file.close()
    finally:
        os.chdir(cwd)

def extractFiles(paths):
    dirs = []
    for path in paths:
        directory = path[0:path.rfind('.')]
        if os.path.exists(directory):
            logger.debug("%s already exists, won't extract again" % directory)
            dirs.append(directory)
            continue
        logger.debug("extracting file %s" % path)
        extractFile(path)
        dirs.append(directory)
    return dirs

def downloadSupportBundles(url):
    urls = processUrl(url)
    if urls is None:
        return "Error: no tgz files found!"
    else:
       hash1 = hashlib.sha1()
       hash1.update(url)
       # new dir name
       newdir = hash1.hexdigest()
       logger.debug("directory name for url %s is %s" % (url, newdir))
       local_paths = downloadFiles(newdir, urls)
       return local_paths

def processUrl(url):
    pattern = r"(?P<number>\d{7})(?P<subpath>(/.*)*)/\*\.tgz"
    p = re.compile(pattern)
    m = p.match(url)
    if m:
        folder_path = URL_PREFIX + '/'.join(list(m.group('number'))) + m.group('subpath')
        urls = getTgzFiles(folder_path)
        return urls
    return None

if __name__ == '__main__':
    url = "1249097/*.tgz"
    local_paths = downloadSupportBundles(url)
    extractFiles(local_paths)
