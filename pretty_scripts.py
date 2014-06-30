#!/usr/bin/python
import sys, re

script_name = sys.argv[1]
html_name = re.sub('\.py$', '.html', script_name)

#whitelist the new file
whitelist = open('whitelist', 'r+b')
new_whitelist = whitelist.read().format('"{}"'.format(html_name)+",{}")
whitelist.seek(0)
whitelist.write(new_whitelist)

f_in = open(script_name)
f_out = open(html_name, 'w')

html = '''\
<!DOCTYPE html>
<html>
<head>
<link href="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.css" rel="stylesheet" type="text/css">
<script src="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.js" type="text/javascript"></script>
</head>
<body onload="prettyPrint()">
<pre class="prettyprint linenums">
{}
</pre>
</body>
</html>
'''

#fix tabs
a = lambda s: s.replace(' '*4, '&nbsp;'*4).replace('\t', '&nbsp;'*4)
#fix < and >
b = lambda s: a(s).replace('<', '&lt;').replace('>', '&gt;')
#fix double quotes
c = lambda s: b(s).replace('"', '&quot;')

f_out.write(html.format(c(f_in.read())))
