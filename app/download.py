import re, os, tarfile, zipfile, hashlib
from urllib2 import urlopen
from bs4 import BeautifulSoup
from mylogger import logger
import subprocess

# config
URL_PREFIX="http://engweb.eng.vmware.com/bugs/files/0/"
LOCAL_DIR="data"

def RunCmd(cmd, env=None):
    p = subprocess.Popen(args=cmd, executable='/bin/bash', stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True, env=env)
    out, err = p.communicate()
    p.poll()
    ret = p.returncode
    return (ret, out, err)

# foler_path: like http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/
# return array of urls for tgz files

def getTgzFiles(folder_path):
    page = BeautifulSoup(urlopen(folder_path).read())
    urls = []
    logger.debug(folder_path)
    for link in page.findAll('a', href=re.compile(r'.*\.tgz')):
        urls.append(folder_path + '/' + link['href'])
    return urls


# url must be fully extended address ending with ".tgz"
def downloadFile(local_new_dir, url):
    filename = os.path.basename(url)
    logger.debug("Downloading " + filename)
    local_path = os.path.abspath(os.path.join(local_new_dir, filename))
    if(os.path.exists(local_path)):
        logger.debug("%s already exists, won't download again" % local_path)
        return local_path

    #req = urlopen(url)
    #CHUNK = 512*1024
    #with open(local_path, 'wb') as f:
    #    while True:
    #        chunk = req.read(CHUNK)
    #        if not chunk: break
    #        f.write(chunk)
    #    f.flush()
    #    f.close()
    ret, out, err = RunCmd('/usr/local/bin/axel -q -n 8 -o %s %s' % (local_path, url))
    if ret != 0:
        raise Exception('Cannot download file: %s, out: %s, err: %s' % (url, out, err))
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
        to_directory = os.path.dirname(path)
        print to_directory
    os.chdir(to_directory)

    try:
        file = opener(path , mode)
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
       for url1 in urls:
           hash1.update(url1)
       # new dir name
       newdir = hash1.hexdigest()
       logger.debug("directory name for url %s is %s" % (url, newdir))
       local_paths = downloadFiles(newdir, urls)
       return local_paths

def parseWildcardTgzUrl(url):
    pattern = r"(?P<number>\d{7})(?P<subpath>(/.*)*)/\*\.tgz"
    p = re.compile(pattern)
    m = p.match(url)
    if m:
        folder_path = URL_PREFIX + '/'.join(list(m.group('number'))) + m.group('subpath')
        urls = getTgzFiles(folder_path)
        return urls
    return None


def processUrl(url):
    url.replace('\n', ' ')
    splits = url.split(' ')
    urls = []
    for split  in splits:
        split = split.strip()
        if split != "":
            if split.startswith('http') and split.endswith('tgz'):
                urls.append(split)
            elif re.match(r'^\d{7}$', split):
                split = split + '/*.tgz'
                urls += parseWildcardTgzUrl(split)
            else:
                print split
                urls += parseWildcardTgzUrl(split)
    return sorted(urls)

if __name__ == '__main__':

    url = "1249097/*.tgz"
    local_paths = downloadSupportBundles(url)
    extractFiles(local_paths)
