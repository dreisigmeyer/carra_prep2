There is significant preprocessing of 2002-2004 patents in 
gbd_cleaner.pl.  This needed to be done because only a subset
of the patent data was being processed and any image files
that the XML files referenced were not there.  This can be
avoided by not calling process02to04 in gbd_cleaner.pl.
There is also corresponding edits of the DTD files in
runit.sh.
