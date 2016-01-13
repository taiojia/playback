package config_test

import (
	"fmt"
	"github.com/nofdev/fastforward/Godeps/_workspace/src/github.com/jiasir/playback/config"
	"testing"
)

var conf config.Config

func TestParse(t *testing.T) {
	conf.Parse()
	v := conf.Openstack_admin_user
	if v != "admin" {
		t.Error("Expected admin, got ", v)
	} else {
		fmt.Println(v)
	}
}

func TestGenConf(t *testing.T) {
	err := conf.GenConf(config.HAPROXYCONFIG, "config_out.conf")
	if err != nil {
		t.Error(err)
	}
}
