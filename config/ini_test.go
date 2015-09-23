package config_test

import (
	"github.com/ccding/go-config-reader/config"
	"testing"
	"fmt"
)

func TestIni(t *testing.T) {
	cfg := config.NewConfig("../inventory/inventory_ha")
	if err := cfg.Read(); err != nil {
		t.Error(err)
	}

	fmt.Println(cfg.Get("openstack", "controller01 ansible_ssh_host"))
}