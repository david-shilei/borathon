import os, sys, inspect, json

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
# note: hash, key is entity, value is an array of logs for that entity
conf = {}

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/timeline1')
def timeline():
#    mydata = {
#	"host": {
#		"host-9:91:76e1b7f8-0-13e9": [
#			{
#				"start": 1231231231123,
#				"line": 234,
#				"file": "hostd.log",
#				"className": "host",
#				"content": "Failed to load virtual machine: vim.fault.FileNotFound",
# 			    "detail":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound." }],
#		"host-9:94:22480d43-0-1ae8": [
#			{
#				"start": 1231231231231,
#				"line": 235,
#				"file": "hostd.log",
#				"className": "host",
#				"content": "Failed to load virtual machine: vim.fault.FileNotFound",
#				"detail": "2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound." }]
#	},
#	"vm": {
#		"vm-esx.0": [
#		{
#			"start": 1231231231123,
#			"line": 234,
#			"file": "hostd.log",
#			"className": "host",
#			"content": "Failed to load virtual machine: vim.fault.FileNotFound",
#		    "detail":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
#		}]
#	}
#    }
    return encode(mydata)

@app.route('/sample')
def sample():
  return render_template('sample.html')

@app.route('/submit', methods=['GET'])
def submit():
    url=request.args.get('url', '')
    return render_template('timeline.html', data = {'url' : url })


@app.route('/timeline', methods=['GET', 'POST'])
def result():
    url=request.args.get('url', '')
    #url = "1249097/*.tgz"
    offset = request.args.get('offset', '0')
    limit = request.args.get('limit', '1000')

    # download and extract support bundles
    local_paths = downloadSupportBundles(url)
    extracted_dirs = extractFiles(local_paths)

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
