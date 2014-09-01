from distutils.core import setup

setup(
    name='zmqdecorators',
    version='0.1dev',
    packages=['zmqdecorators',],
    license='GNU LGPL',
    long_description=open('README.md').read(),
    install_requires=[
        'tornado>=2.0',
        'pyzqm=>2.0',
        'pybonjour=>1.1',
    ],
)

