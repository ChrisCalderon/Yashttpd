import sys, os

file_to_add = sys.argv[1]
message = sys.argv[2]
assert os.path.exists(file_to_add)

page = '''\
<html>
<head>
<link href="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.css" rel="stylesheet" type="text/css"/>
<script src="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.js" type="text/javascript"></script>
</head>
<body onload="prettyPrint()">
<pre class="prettyprint linenums">
{}
</pre>
</body>
</html>'''

link_to_page = '<p>{} <a href="{}">here</a>!</p>\n'.format(message, file_to_add+'.html')
link_to_page += '{1}'

handler_script = open('myhandler.py', 'r+b')
f_in = open(file_to_add)
f_out = open(file_to_add + '.html', 'wb')

old_script = handler_script.read()
new_script = old_script.format('\''+file_to_add+'.html\',\n    {0}', link_to_page)
handler_script.seek(0)
handler_script.write(new_script)

a = lambda x: x.replace('<', '&lt;').replace('>', '&gt;')
b = lambda x: a(x).replace('\t', '&nbsp;'*4).replace(' '*4, '&nbsp;'*4)
c = lambda x: b(x).replace('"', '&quot;')

f_out.write(page.format(c(f_in.read())))

sys.exit(1)
