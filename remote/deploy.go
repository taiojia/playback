// The MIT License (MIT)
//
// Copyright (c) 2015 Taio Jia (jiasir) <taio@outlook.com>
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package remote

import "github.com/wingedpig/loom"

// The provisioning interface
type Provisioning interface {
	Execute(c Cmd) (string, error)
}

// Config contains ssh and other configuration data needed for all the public functions in playback
type Conf struct  {
	loom.Config
}

// To make the config for ssh login for instance
func MakeConfig(user, host string, output, abort bool) (*Conf, error) {
	return &Conf{loom.Config{User: user, Host: host,
		DisplayOutput: output, AbortOnError: abort}}, nil
}

// Execute command line
type Cmd struct {
	// Using apt-get update if set to true
	AptCache bool

	// Command line to execute
	CmdLine string

	// Using sudo to execute command line
	UseSudo bool

}

// Execute the command
func (c *Conf) Execute(d Cmd) (string, error) {
	if d.AptCache {
		c.Sudo("apt-get update")
	}
	if d.UseSudo {
		c.Sudo(d.CmdLine)
	} else {
		c.Run(d.CmdLine)
	}
	return "", nil
}