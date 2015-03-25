define tune_fs::change_mountpoint($mountpoint_count = 1, $current = 1, $fs_mount, $fs_option, $state) {
  if ($current != $mountpoint_count) {
    $c_num = $current + 1
    tune_fs::change_mountpoint{ "${name}_${fs_mount}_${current}_${fs_option}":
      mountpoint_count => $mountpoint_count,
      current          => $c_num,
      fs_mount         => $fs_mount,
      fs_option        => $fs_option,
      state            => $state,
    }
  }

  tune_fs::set_mountpoint_option{ "${name}_${fs_option}_$fs_mount_${current-1}":
    mount            => "$fs_mount${current-1}",
    option           => $fs_option,
    state            => $state,
  }
}