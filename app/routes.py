import os, sys, inspect
# realpath() with make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from flask import Flask, render_template, url_for, request, jsonify, session
from util import downloadFiles, processUrl, extractFiles
from pprint import pprint
from processlog import processLog

app = Flask(__name__)
PATTERN_FILE = "patterns.txt"
THREAD_ENTITY_FILE = "thread_entity.txt"
supported_logs = ["hostd.log"]
patterns = dict()
thread_entity_patterns = dict()

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/test')
def test():
    return jsonify(username="txie", id="1")

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/')
def index():
    return "index"

@app.route('/login')
def login():
    return "login"

@app.route('/user/<username>')
def profile(username):
    return "username"


@app.route('/submit', methods=['GET'])
def submit():
    url=request.args.get('url', '')

    # download and extract support bundles
    urls = processUrl(url.strip())
    local_paths = downloadFiles(urls)
    extracted_dirs = extractFiles(local_paths)
    extracted_dirs = ['/Users/seanzhao/Downloads/esxlog']

    session['extracted_dirs'] = extracted_dirs
    processLog(extracted_dirs, supported_logs, patterns, thread_entity_patterns)
    #xxx: Pre-process log data according to patterns in patterns.txt.
    #     return json data to be used in timeline graph
    return "support bundles has been uploaded! <br>" + \
           '<br>'.join(extracted_dirs)

@app.route('/testsession')
def testsession():
    #pprint(session['local_paths'])
    return "You have uploaded these support bundles <br>" +  \
           '<br>'.join(session['extracted_dirs'])

def loadPatterns():
    patterns['hostd.log'] = []
    patterns['vmkernel.log'] = []
    thread_entity_patterns['hostd.log'] = []
    thread_entity_patterns['vmkernel.log'] = []

    with open(PATTERN_FILE) as f:
        content = f.readlines()
    f.close()
    for line in content:
        line.strip()
        if line.startswith("hostd.log:"):
            patterns['hostd.log'].append(line.lstrip("hostd.log:"))
        elif line.startswith("vmkernel.log:"):
            patterns['vmkernel.log'].append(line.lstrip("vmkernel.log"))
        else:
            pass
    with open(THREAD_ENTITY_FILE) as f:
        content = f.readlines()
    f.close()
    for line in content:
        line.strip()
        if line.startswith("hostd.log:"):
            thread_entity_patterns['hostd.log'].append(line.lstrip("hostd.log:"))
        elif line.startswith("vmkernel.log:"):
            thread_entity_patterns['vmkernel.log'].append(line.lstrip("vmkernel.log"))
        else:
            pass

if __name__ == '__main__':
    loadPatterns()
    pprint(patterns)
    app.run(debug=True)
