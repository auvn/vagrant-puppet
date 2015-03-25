class timezone( $zone="Asia/Yekaterinburg" ){
    file { "timezone":
		path => "/etc/sysconfig/clock",
		ensure => present,
		content => template("timezone/timezone-centos"),
	}
    exec {
	"set-timezone":
	    command => "/usr/sbin/tzdata-update",
	    require => File["timezone"],
	    subscribe => File["timezone"],
	    refreshonly => true,
	}
}