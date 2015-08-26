package main


import (
	"github.com/jiasir/playback/libs/azure-sdk-for-go/management"
	"github.com/jiasir/playback/libs/azure-sdk-for-go/management/hostedservice"
	"encoding/base64"
)

func main() {
	dnsName := "test-vm-from-go"
	location := "China East"


	client, err := management.ClientFromPublishSettingsFile("/Users/Taio/Downloads/Microsoft_Azure_credentials.publishsettings", "")
	if err != nil {
		panic(err)
	}

	// create hosted service
	if err := hostedservice.NewClient(client).CreateHostedService(hostedservice.CreateHostedServiceParameters{
		ServiceName: dnsName,
		Location:    location,
		Label:       base64.StdEncoding.EncodeToString([]byte(dnsName))}); err != nil {
		panic(err)
	}
}

