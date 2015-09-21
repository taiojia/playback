package main

import "github.com/spf13/cobra"
import "fmt"
import "strings"


func main()  {
	var PostgreSql = &cobra.Command{
		Use:   "deploy-postgresql",
		Short: "Deploy PostgreSQL",
		Long: `Deploy PostgreSQL`,
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Print: " + strings.Join(args, " "))
		},
	}
	PostgreSql.Execute()
}