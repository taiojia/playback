package main

import (
"fmt"
"os"
"os/exec"
"log"
)


func main() {
	if run, err := exec.Command("exiftool", "-overwrite_original", "-r", "-all=", os.Args[1:]...).Output(); err != nil {
		log.Fatal(err)
	} else {
		fmt.Println(string(run))
	}
}