python-zmqdecorators
====================

Decorators for pyZMQ to make it almost as easy to use a DBUS (requires Bonjour for discovery magic)


Forked from <https://github.com/HelsinkiHacklab/reactor>

## Requirements

    sudo apt-get install python python-pip python-zmq python-tornado libavahi-compat-libdnssd1
    sudo pip install pybonjour || sudo pip install --allow-external pybonjour --allow-unverified pybonjour pybonjour 

Though pybonjour will be installed by pip automagically if you install this package with pip. 

Remember to enable global site packages for the ZMQ bindings if using virtualenv.

Pro tip for thos wishing to work on the code <http://guide.python-distribute.org/pip.html#installing-from-a-vcs> (short version checkout then `pip install -e ./`)
