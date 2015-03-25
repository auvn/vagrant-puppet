define tune_fs::change_mountoption($mountpoint_count = 1, $current = 1, $fs_mount, $fs_options, $state) {
  $options_count = size($fs_options)

  if ($current != $options_count) {
    $c_num = $current + 1
    tune_fs::change_mountoption{ "${name}_${fs_mount}_${current}":
      mountpoint_count => $mountpoint_count,
      current          => $c_num,
      fs_mount         => $fs_mount,
      fs_options       => $fs_options,
      state            => $state,
    }
  }

  tune_fs::change_mountpoint { "${name}_${current}_${mountpoint_count}":
    mountpoint_count => $mountpoint_count,
    fs_mount         => $fs_mount,
    fs_option        => $fs_options[$current-1],
    state            => $state,
  }
}