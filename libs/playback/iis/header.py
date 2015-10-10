__author__ = 'jiasir'

import os
import subprocess
import socket


def add_header(site_name='Default Web Site', header_name='X-Served-By', app_name='www', ip='1.2.3.4'):
    """
    add http response header to iis
    :param site_name: iis web site
    :param header_name: which header to be added
    :param app_name: application name
    :param ip: local ip
    :return: None
    """
    os.system(
        'c:\\windows\\system32\\inetsrv\\appcmd.exe set config "{site_name}" -section:system.webServer/httpProtocol /+"customHeaders.[name=\'{header_name}\',value=\'{app_name}>>{ip}\']"'.format(
            site_name=site_name, header_name=header_name, app_name=app_name, ip=ip))


def get_sites():
    """
    get all sites
    :return: a list of sites
    """
    output = subprocess.Popen(['c:\\windows\\system32\\inetsrv\\appcmd.exe', 'list', 'site'],
                              stdout=subprocess.PIPE).communicate()[0]

    sites = []
    for line in output.split(os.linesep):
        if line != '':
            site = line.split('"')[1]
            sites.append(site)
    return sites


def get_ip():
    """
    get the host ip
    :return: string of ip
    """
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


def main():
    try:
        os.system(
            'c:\\windows\\system32\\inetsrv\\appcmd.exe set config -section:system.webServer/httpProtocol /-"customHeaders.[name=\'X-Powered-By\']"')
    except:
        pass

    sites = get_sites()
    for s in sites:
        add_header(site_name=s, app_name=s, ip=get_ip())


if __name__ == '__main__':
    main()
