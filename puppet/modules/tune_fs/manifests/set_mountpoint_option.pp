define tune_fs::set_mountpoint_option($mount, $option, $state) {
  exec { "${name}_execute_remount_${mount}_${option}":
    command            => "mount $mount -o remount",
    path               => "/bin/",
    refreshonly        => true,
  }

  case $state {
    'set': {
      augeas{ "${name}-fstab-$mount-$option":
        context        => "/files/etc/fstab/*[file = '$mount'][count(opt[. = '$option']) = 0]",
        changes        => [
          "ins opt after opt[last()]",
          "set opt[last()] $option"
        ],
        onlyif         => "match /files/etc/fstab/*[file = '$mount'][count(opt[. = '$option']) = 0] size > 0",
        notify         => Exec["${name}_execute_remount_${mount}_${option}"],
      }
    }
    'remove': {
      augeas{ "${name}-fstab-$mount-$option":
        context        => "/files/etc/fstab/*[file = '$mount'][count(opt[. = '$option']) = 1]",
        changes        => [ "rm opt[. = '$option']" ],
        onlyif         => "match /files/etc/fstab/*[file = '$mount'][count(opt[. = '$option']) = 1] size > 0",
        notify         => Exec["${name}_execute_remount_${mount}_${option}"],
      }
    }
  }
}