package main

import (
	"fmt"
	"os"
	"os/exec"
	"log"
)

func main() {
	if playbackRun, playbackRunErr := exec.Command("ansible-playbook", os.Args[1:]...).Output(); playbackRunErr != nil {
		log.Fatal(playbackRunErr)
	} else {
		fmt.Println(string(playbackRun))
	}
}