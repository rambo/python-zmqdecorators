from distutils.core import setup
import subprocess

git_version = str(subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD'])).strip()

setup(
    name='zmqdecorators',
    version='0.5.dev-%s' % git_version,
    packages=['zmqdecorators',],
    license='GNU LGPL',
    long_description=open('README.md').read(),
    install_requires=[
        'tornado>=2.0',
        'pyzqm=>2.0',
        'pybonjour=>1.1',
    ],
    url='https://github.com/rambo/python-zmqdecorators',
)

