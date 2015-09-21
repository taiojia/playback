package config_test

import (
	"github.com/jiasir/playback/config"
	"testing"
	"fmt"
)

func TestParse(*testing.T) {
	var config config.Config
	config.Parse()
	fmt.Println(config.Openstack_admin_user, config.Openstack_admin_pass)
}