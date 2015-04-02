from string import Template

def config():
    config = {
        'vm_mem' : '128',
        'vm_box_name' : 'puppetlabs/centos-6.6-32-puppet',

	'ssh_app_username' : 'app_user',
	'ssh_app_password' : 'app_user',

        'master_name': 'vm-cluster-node1',
        'master_ip': '10.211.55.201',
	'master_port' : '8080',

        'slave1_name': 'vm-cluster-node2',
        'slave1_ip': '10.211.55.202',

        'slave2_name': 'vm-cluster-node3',
        'slave2_ip': '10.211.55.203',
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
