from distutils.core import setup
import subprocess

setup(
    name='zmqdecorators',
    version='0.5.dev-' + subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD']),
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

