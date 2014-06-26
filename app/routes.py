import os, sys, inspect

import processlog
import json
from flask import Flask, render_template, url_for, request, session, abort, Response
from download import downloadFiles, processUrl, extractFiles, downloadSupportBundles
from pprint import pprint
from jsonpickle import encode
from processlog import processLog, getNLines
from mylogger import logger

app = Flask(__name__)

PATTERN_CONFIG = "patterns.conf"
LOG_PATTERN_FILE = "log_patterns.txt"
ENTITY_PATTERN_FILE = "entity_patterns.txt"
THREAD_ENTITY_FILE = "thread_entity.txt"
# note: hash, key is entity, value is an array of logs for that entity
conf = {}

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/sample')
def sample():
  return render_template('sample.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
    url=request.args.get('url', '')
    #url = "1249097/*.tgz"
    offset = request.args.get('offset', '0')
    limit = request.args.get('limit', '1000')

    # download and extract support bundles
    local_paths = downloadSupportBundles(url)
    extracted_dirs = extractFiles(local_paths)

    session['extracted_dirs'] = extracted_dirs

    mapping = processLog(extracted_dirs, conf['patterns'], int(offset), int(limit))
    #pprint(mapping)

    return encode(mapping)

@app.route('/patterns')
def patterns():
    return encode(conf['patterns'])

@app.route('/testsession')
def testsession():
    #pprint(session['local_paths'])
    return "You have uploaded these support bundles <br>" +  \
           '<br>'.join(session['extracted_dirs'])

@app.route('/raw')
def raw():
    _check_required_fields(request, 'file', 'linenum')
    file_name = request.args.get('file')
    line_num = int(request.args.get('linenum'))
    default_n = 5
    n = int(request.args.get('n')) if request.args.get('n') is not None else default_n
    return getNLines(file_name, line_num, n)

@app.route('/bugzilla/<entity>')
def get_bugzilla_records(entity):
   rv = processlog.getBugzillaRecords(entity)
   return Response(json.dumps(rv),  mimetype='application/json')

def _check_required_fields(request, *fields):
    if request.args is None:
       logger.info('No args fields.')
       abort(400)
    for field in fields:
       if request.args.get(field) is None:
          logger.info('Missing required args.')
          abort(400)

def loadPatterns():
    execfile(PATTERN_CONFIG, conf)

if __name__ == '__main__':
    loadPatterns()
    app.run(debug=True)
