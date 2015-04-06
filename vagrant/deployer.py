
from setuptools.command import easy_install
import sys
import json
import argparse
import os
from fabric.api import *
import vagrant
import httplib



vgrnt = vagrant.Vagrant()

data = {}

def get_vms():
    if not 'vms' in data:
        vms = [status.name for status in vgrnt.status() if status.state == vgrnt.RUNNING]
        data['vms'] = vms
    return data['vms']

def get_ssh_opts(name):
    if not name:
        return None
    return vgrnt.conf(vm_name=name)

def get_vm_connections():
    if not 'vm_connections' in data:
        vm_connections = dict(zip(get_vms(), [get_ssh_opts(vm) for vm in get_vms()]))
        data['vm_connections'] = vm_connections
    return data['vm_connections']

def config():
    if not 'config' in data:
        data['config'] = json.loads(open('../config.json').read())
    return data['config']

def get_vm_name(connection):
    return "%s" % connection['Host']

def get_host(connection):
    vm_name = get_vm_name(connection)
    return vgrnt.user_hostname_port(vm_name=vm_name)

def get_hosts_dict(*args):
    return {get_host(conn): conn for conn in get_vm_connections().values()}

def get_key_filename(connection):
    vm_name = get_vm_name(connection)
    return "%s" % vgrnt.keyfile(vm_name=vm_name)

def url_response(ip, port, path):
    http_connection = httplib.HTTPConnection('%s:%s' % (ip, port))
    try:
        http_connection.request('GET', path)
    except Exception as e:
        return False, "%s" % e
    resp = http_connection.getresponse()
    if resp.status == 200:
        return True, resp.read()
    else:
        return False, resp.read()
    return False, None

############# IMPLEMENTATION ##############

def publish_app_task(task_args):
    jar_file = task_args['jar']

    if not os.path.isfile(jar_file):
        abort("'%s' doesn't exist." % jar_file)

    jar_file_name = os.path.basename(jar_file)
    if not jar_file_name.endswith('.jar'):
        abort("Looks like '%s' is not a jar file." % jar_file_name)

    conf = config()

    app_name = 'app'

    app_directory = conf['apps'][app_name]['dir']

    target_file = "%s/%s.jar" % (app_directory, app_name)

    app_port = conf['apps'][app_name]['port']

    command = "java -jar %s --server.port=%s" % (target_file, app_port)

    run('pkill -f "%s"' % command)
    put(jar_file, target_file)
    run('nohup %s > %s/%s.log &' % (command, app_directory, app_name), pty=False)

def test_app_url(task_args):
    conf = config()
    app_name = 'app'
    connection = get_hosts_dict()[env.host_string]
    vm_name = get_vm_name(connection)
    ip = conf['hosts'][vm_name]['ip']
    port = conf['apps'][app_name]['port']
    path = '/'
    status, resp = url_response(ip, port, path)
    if status:
        puts("App is running. Response: %s" % resp, end='\r\n')
    else:
        puts("App isn't running. Response: %s" % resp, end='\r\n')


############# IMPLEMENTATION ###############

def prepare_connection(function, connections, args):
    vm_name = env.host_string
    connection = connections[vm_name]   
    host = get_host(connection)
    
    args['vm_name'] = vm_name

    key_filename = get_key_filename(connection)
    with settings(key_filename=key_filename, warn_only=True):
        execute(function, host=host, task_args = args)

def do_fabric(function, args):
    with settings(parallel=False, warn_only=True, hosts = args['hosts']):
        execute(prepare_connection, function=function, connections = get_vm_connections(), args=args)


######## ARGUMENT COMMANDS ##########
def list_hosts(args):
    vms = get_vms()
    print "Available hosts: ", vms

def install_app(args):
    do_fabric(publish_app_task, args)

def test_app(args):
    do_fabric(test_app_url, args)

######## ARGUMENT COMMANDS ##########


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Deployer')
    arg_parser.add_argument('--hosts', help='list of hosts for deployment using comma')
    actions = arg_parser.add_subparsers(title='Available actions')
    
    list_hosts_action = actions.add_parser('available_hosts', help='Show available hosts for any action')
    list_hosts_action.set_defaults(func=list_hosts)

    install_action = actions.add_parser('install', help='Install a jar to specified host')
    install_action.add_argument('jar')
    install_action.set_defaults(func=install_app)

    test_action = actions.add_parser('test', help='Test the installed app')
    test_action.set_defaults(func=test_app)

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
