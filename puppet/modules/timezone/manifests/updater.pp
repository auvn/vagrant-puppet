class timezone::updater {

  $tzupdater = '/usr/sbin/tzupdater.jar'
  notify{'timezone_updater':
    message => 'updating timezone',
  }
  ->
  file { $tzupdater:
    ensure  => file,
    source  => 'puppet:///modules/timezone/tzupdater.jar',
  }
  ->
  exec { "tzupdate":
    unless => "/usr/bin/java -jar $tzupdater -t",
    command => "/usr/bin/java -jar $tzupdater -u",
    user => root,
  }
}
