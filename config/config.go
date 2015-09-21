// the config package is that OpenStack configuration
// this configuration is the yaml file "../vars/openstack/openstack.yml"
package config

import (
	"gopkg.in/yaml.v2"
	"io/ioutil"
)

// The the location for configuration file of playback
const CONFIGFILE string = "../vars/openstack/openstack.yml"

// The configuration of OpenStack
// Each var is the key
type Config struct {
	Openstack_admin_user string
	Openstack_admin_pass string
}

// Parsing yaml
// Return the Config struct
func(c *Config) Parse() (Config){
	source, err := ioutil.ReadFile(CONFIGFILE); if err != nil {
		panic(err)
	}
	err = yaml.Unmarshal(source, &c); if err != nil {
		panic(err)
	}
	return *c
}