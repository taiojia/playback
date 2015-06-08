package main

import (
	"fmt"
	"os"
	"os/exec"
	"log"
)

func main() {
	playbackRun, playbackRunErr := exec.Command("ansible-playbook", os.Args[1:]...).Output()

	if playbackRunErr != nil {
		log.Fatal(playbackRunErr)
	}
	fmt.Println(string(playbackRun))
}