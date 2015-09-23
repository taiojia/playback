package config_test

import (
	"github.com/jiasir/playback/config"
	"testing"
	"fmt"
)

var conf config.Config

func TestParse(t *testing.T) {
	conf.Parse()
	v:= conf.Openstack_admin_user; if v != "admin"{
		t.Error("Expected admin, got ", v)
	} else {
		fmt.Println(v)
	}
}

func TestGenConf(*testing.T) {
	conf.GenConf("template.conf")
}