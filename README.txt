Author: Lyron Juan Winderbaum
Date  : 26/3/2015

I wrote dat2tex in order to extract useful 
information from a mascot search result (.dat) 
file, and print it out in a .tex file to be 
compiled into a pretty LaTeX pdf. :)

I am using msparser distribution version 2.5.0
for Python 2.7. msparser is provided by 
Matrix Science, and they own the copyright to it 
etc. I think.

TODO:
 - Add an option to call a subprocess and compile 
	the .tex into a .pdf
 - Move the printing to a function, which is then
	called from main()
 - Add an index to keep track of indentation 
	(semi-)automatically.
