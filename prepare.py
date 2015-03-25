from string import Template

def config():
    config = {
        'master_name': 'vm-cluster-node1',
        'slave1_name': 'vm-cluster-node2',
        'master_ip': '10.211.55.201',
        'slave1_ip': '10.211.55.202',
    }
    return config

if __name__ == "__main__":
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
