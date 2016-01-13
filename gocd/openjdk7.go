package main

import "github.com/nofdev/fastforward/Godeps/_workspace/src/github.com/jiasir/playback/libs/command"

func main() {
	if err := command.Command("sudo", "apt-get", "install", "-y", "openjdk-7-jdk"); err != nil {
		panic(err)
	}
}
