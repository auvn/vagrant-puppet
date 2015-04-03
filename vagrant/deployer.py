
from setuptools.command import easy_install
import sys
import json
import argparse
import os


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

data = {}

def get_vms():
    if not 'vms' in data:
        vms = [status.name for status in vgrnt.status() if status.state == 'running']
        data['vms'] = vms
    return data['vms']

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

def get_vm_connections():
    if not 'vm_connections' in data:
        vm_connections = dict(zip(get_vms(), [get_ssh_opts(vm) for vm in get_vms()]))
        data['vm_connections'] = vm_connections
    return data['vm_connections']

def config():
    return json.loads(open('../config.json').read())

def get_host(connection):
    return "%s@%s:%s" % (connection['User'], connection['HostName'], connection['Port'])

def get_hosts_dict(*args):
    return {get_host(conn): conn for conn in get_vm_connections().values()}

def get_vm_name(connection):
    return "%s" % connection['Host']

def get_key_filename(connection):
    return "%s" % connection['IdentityFile']

############# IMPLEMENTATION ##############

def publish_app(args):

    task_args = args['args']
    jar_file = task_args['jar']

    if not os.path.isfile(jar_file):
        abort("'%s' doesn't exist." % jar_file)

    connections = args['vm_connections']
    vm_name = env.host_string
    connection = connections[vm_name]

    host = get_host(connection)
    key_filename = get_key_filename(connection)

    app_directory = config()['app_directory']
    app_directory = '~/'

    with settings(host_string=host, key_filename=key_filename):
        run("ls -l %s/%s" % (app_directory, jar_file)

############# IMPLEMENTATION ###############

def do_fabric(function, args):
    with settings(parallel=False, warn_only=True):
        execute(function, hosts = args['hosts'], args = {'vm_connections' : get_vm_connections(), 'args' : args})

def list_hosts(args):
    vms = get_vms()
    print "Available hosts: ", vms

def install_app(args):
    do_fabric(publish_app, args)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Deployer')
    arg_parser.add_argument('--hosts', help='list of hosts for deployment using comma')
    actions = arg_parser.add_subparsers(title='Available actions')
    
    list_hosts_action = actions.add_parser('available_hosts', help='Show available hosts for any action')
    list_hosts_action.set_defaults(func=list_hosts)

    install_action = actions.add_parser('install', help='Install a jar to specified host')
    install_action.add_argument('--jar', required=True)
    install_action.set_defaults(func=install_app)


    args = vars(arg_parser.parse_args())
    
    hosts = args['hosts']
    if not hosts:
        hosts = get_vms()
    else:
        hosts = hosts.strip().split(',')
        running_hosts = get_vms()
        for host in list(hosts):
            if not host in running_hosts:
                print "'%s' is down. Skipping." % host
                hosts.remove(host)
            
    args['hosts'] = hosts
    function  = args.pop('func')
    function(args)
