package command

import "os/exec"
import "bytes"

import "fmt"

func Command(args ...string) error{
	cmd := exec.Command("/usr/bin/env", args...)
	var out bytes.Buffer
	cmd.Stdout = &out

	if err := cmd.Run(); err != nil {
		return err
	}

	fmt.Println(out.String())
	return nil
}
