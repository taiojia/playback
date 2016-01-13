package main

import (
	"github.com/nofdev/fastforward/Godeps/_workspace/src/github.com/jiasir/playback/command"
	"os"
)

func main() {
	command.ExecuteWithOutput("ansible-playbook", os.Args[1:]...)
}
