from string import Template
import string
import json
from setuptools.command import easy_install

def check_module(module, package):
    if not package:
        return None
    if not module:
        return None
    try:
        __import__(module)
    except ImportError:
        install(package)

class FormatDict(dict):
    def __missing__(self, key):
        return "{%s}" % key

def install(package):
    if not package:
       return None
    easy_install.main(['-q','-U', package])

def dependencies():
    check_module('vagrant','python_vagrant')
    check_module('Crypto','pycrypto')
    check_module('fabric','fabric')

def config():
    config = json.loads(open('./config.json').read())
    return config

def prepare_config(tmpl_file_name, out_file_name, conf):
    with open (tmpl_file_name, "r") as tmpl_file:
        tmpl = tmpl_file.read()
	tmpl = tmpl.replace('{', "{{").replace('}', "}}").replace('<[' , '{').replace(']>', '}')
        content = string.Formatter().vformat(tmpl, (), FormatDict(**conf))
        out_file = open(out_file_name, "w")
        out_file.write(content)



if __name__ == '__main__':
    dependencies()
    conf = config()
    prepare_config("vagrant/Vagrantfile.tmpl", "vagrant/Vagrantfile", conf)
    prepare_config("puppet/manifests/site.pp.tmpl", "puppet/manifests/site.pp", conf)
