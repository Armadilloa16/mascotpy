Author: Lyron Juan Winderbaum
Date  : 26/3/2015

I wrote mascotpy in order to extract useful 
information from a mascot search result (.dat) 
file, and print it out in a .tex file to be 
compiled into a pretty LaTeX pdf. :)

testingDriver is a simple script for testing 
use of mascotpy as a module, as opposed to 
from the commandline.

I am using msparser distribution version 2.5.0
for Python 2.7. msparser is provided by 
Matrix Science, and they own the copyright to it 
etc. I think. I have not included msparser
itself in this repo as it is neccessary to use 
different versions of msparser depending on what
system you are running (linux/windows), and 
depending on if you are running a 32/64bit 
system. It can be downloaded from the Matrix 
Science website.

TODO:
 - Add an option to call a subprocess and compile 
	the .tex into a .pdf
 - Add an index to keep track of indentation 
	(semi-)automatically.
