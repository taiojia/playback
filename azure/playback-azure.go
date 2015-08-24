package main


import (
	"github.com/jiasir/playback/libs/azure-sdk-for-go/management/location"
	"github.com/jiasir/playback/libs/azure-sdk-for-go/management"
)

func main() {
	if client, err := management.ClientFromPublishSettingsFile("/Users/Taio/Downloads/Microsoft_Azure_credentials.publishsettings", ""); err != nil {
		panic(err)
	}

}

