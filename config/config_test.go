package config_test

import (
	"github.com/jiasir/playback/config"
	"testing"
	"fmt"
)

func TestParse(t *testing.T) {
	var config config.Config
	config.Parse()
//	fmt.Println(config.Openstack_admin_user, config.Openstack_admin_pass)
	v:= config.Openstack_admin_user; if v != "admin"{
		t.Error("Expected admin, got ", v)
	} else {
		fmt.Println(v)
	}
}