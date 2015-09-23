package main

import (
	"github.com/jiasir/playback/command"
	"os"
)

func main() {
	command.ExecuteWithOutput("ansible-playbook", os.Args[1:]...)
}