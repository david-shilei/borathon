These are the command-line Code Search tools from
https://code.google.com/p/codesearch.

These binaries are for 64-bit x86 systems running Mac OS X.

To get started, run cindex with a list of directories to index:

	cindex /usr/include $HOME/src

Then run csearch to run grep over all the indexed sources:

	csearch DATAKIT

For details, run either command with the -help option, and
read http://swtch.com/~rsc/regexp/regexp4.html.
