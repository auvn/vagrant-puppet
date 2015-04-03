from string import Template
import json

def check_module(module, package):
    if not package:
        return None
    if not module:
        return None
    try:
        __import__(module)
    except ImportError:
        install(package)

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

if __name__ == '__main__':
    dependencies()
    conf = config()
    with open ("vagrant/Vagrantfile.tmpl", "r") as vagrantTmlFile:
        vagrantTmpl = vagrantTmlFile.read()
        content = Template(vagrantTmpl).safe_substitute(conf)
        vagrantFile = open("vagrant/Vagrantfile", "w")
        vagrantFile.write(content)

    with open ("puppet/manifests/site.pp.tmpl", "r") as siteTmlFile:
        siteTmpl = siteTmlFile.read()
        content = Template(siteTmpl).safe_substitute(conf)
        siteFile = open("puppet/manifests/site.pp", "w")
        siteFile.write(content)
