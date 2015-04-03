
from setuptools.command import easy_install
import sys


def install(package):
    if not package:
       return None
    easy_install.main(['-q','-U',package])

def check_module(module, package):  
    if not package:
	return None
    if not module:
	return None
    try:
	__import__(module)
    except ImportError:
        install(package)

check_module('vagrant','python_vagrant')
check_module('Crypto','pycrypto')
check_module('fabric','fabric')

from fabric.api import *
import vagrant


vgrnt = vagrant.Vagrant()


vms = [status.name for status in vgrnt.status() if status.state == 'running']

def get_ssh_opts(name):
    if not name:
        return None
    ssh_config = None
    try:
        ssh_config = vgrnt.ssh_config(name).split()
    except Exception:
        return None
    opts = dict(zip(ssh_config[::2], ssh_config[1::2]))
    return opts


vm_connections = dict(zip(vms, [get_ssh_opts(vm) for vm in vms]))

def get_host(connection):
    return "%s@%s:%s" % (connection['User'], connection['HostName'], connection['Port'])

def get_hosts_dict(*args):
    return {get_host(conn): conn for conn in vm_connections.values()}

def get_vm_name(connection):
    return "%s" % connection['Host']

def get_key_filename(connection):
    return "%s" % connection['IdentityFile']





def publish_app(kwargs):
    connections = kwargs['vm_connections']
    vm_name = env.host_string
    connection = connections[vm_name]


    host = get_host(connection)
    key_filename = get_key_filename(connection)

    with settings(parallel=True, host_string=host, key_filename=key_filename):
	run("uname -a")

def main(args):

    targets = vms
    execute(publish_app ,hosts = targets, kwargs = {'vm_connections' : vm_connections})

if __name__ == '__main__':
    main(sys.argv)
