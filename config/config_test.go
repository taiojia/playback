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

func TestGenConf(t *testing.T) {
	err := conf.GenConf(config.HAPROXYCONFIG, "config_out.conf"); if err != nil {
		t.Error(err)
	}
}