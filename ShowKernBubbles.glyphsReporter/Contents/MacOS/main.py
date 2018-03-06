def _run(script):
	global __file__
	import os, sys
	sys.frozen = 'macosx_plugin'
	base = os.environ['RESOURCEPATH']
	__file__ = path = os.path.join(base, script)
	if sys.version_info[0] == 2:
		with open(path, 'rU') as fp:
			source = fp.read() + "\n"
	else:
		with open(path, 'r', encoding='utf-8') as fp:
			source = fp.read() + '\n'

	exec(compile(source, script, 'exec'), globals(), globals())

_run('plugin.py')
