### Example: Microsoft Windows image
This example creates a Windows Server 2012 qcow2 image, using `virt-install` and the KVM hypervisor.

* Follow these steps to prepare the installation:
    * Download a Windows Server 2012 installation ISO. Evaluation images are available on the Microsoft website (registration required).
    * Download the signed VirtIO drivers ISO from the [Fedora website](https://fedoraproject.org/wiki/Windows_Virtio_Drivers).
    * Create a 50 GB qcow2 image:

        $ qemu-img create -f qcow2 ws2012.qcow2 50G
    
    * Start the Windows Server 2012 installation with the `virt-install` command:
        
        # virt-install --connect qemu:///system \
        --name ws2012 --ram 2048 --vcpus 2 \
        --network network=default,model=virtio \
        --disk path=ws2012.qcow2,format=qcow2,device=disk,bus=virtio \
        --cdrom /path/to/en_windows_server_2012_x64_dvd.iso \
        --disk path=/path/to/virtio-win-0.1-XX.iso,device=cdrom \
        --vnc --os-type windows --os-variant win2k8

    * Use `virt-manager` or `virt-viewer` to connect to the VM and start the Windows installation.
    * Enable the VirtIO drivers.
        * The disk is not detected by default by the Windows installer. When requested to choose an installation target, click `Load driver` and browse the file system to select the `E:\WIN8\AMD64` folder. The Windows installer displays a list of drivers to install. Select the VirtIO SCSI and network drivers, and continue the installation.
    * Log in as administrator and start a command window. Complete the VirtIO drivers installation by running the following command:
        
        pnputil -i -a E:\WIN8\AMD64\*.INF
        
    * To allow `Cloudbase-Init` to run scripts during an instance boot, set the PowerShell execution policy to be unrestricted:
        
        Set-ExecutionPolicy Unrestricted
        
    * Download and install Cloudbase-Init:
    
        Invoke-WebRequest -UseBasicParsing http://www.cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi -OutFile c:\cloudbaseinit.msi
        c:\cloudbaseinit.msi
        
    * In the configuration options window, change the following settings (DO NOT using the `metadata password`, it is a bug:
    
        * Username: `Administrator`
        * Network adapter to configure: `Red Hat VirtIO Ethernet Adapter`
        * Serial port for logging: `COM1`
        
    * When the installation is done, in the `Complete the Cloudbase-Init Setup Wizard` window, select the `Run Sysprep` and `Shutdown` check boxes and click `Finish`.
    
    * Wait for the machine shutdown.
    
    * Your image is ready to upload to the Image service:
    
        $ glance image-create --name WS2012 --disk-format qcow2 \
        --container-format bare --is-public true \
        --file ws2012.qcow2
        