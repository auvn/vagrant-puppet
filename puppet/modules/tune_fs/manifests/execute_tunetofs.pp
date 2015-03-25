define tune_fs::execute_tunetofs {
  file { '${name}_tunetofs_file':
    path      => "/tmp/tunetofs.sh",
    content   => "#!/bin/bash
		    	for device in `ls /dev/sd* | grep '/dev/sd[a-z].'`; do
		    	  tune2fs -m 0 \$device
		        tune2fs -O ^has_journal \$device
		    	done",
    mode      => '+x',
    owner     => "root",
    notify    => Exec["execute_tunetofs"],
  }

  exec { "${name}_execute_tunetofs":
    command      => "/tmp/tunetofs.sh",
    user         => root,
    path         => "/tmp/",
    refreshonly  => false,
  }
}