#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, NTT Ltd.
#
# Author: Ken Sinfield <ken.sinfield@cis.ntt.com>
#
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'NTT Ltd.'
}

DOCUMENTATION = '''
---
module: server_info
short_description: Get and List Servers
description:
    - Get and List Servers
version_added: "2.10"
author:
    - Ken Sinfield (@kensinfield)
options:
    auth:
        description:
            - Optional dictionary containing the authentication and API information for Cloud Control
        required: false
        type: dict
        suboptions:
            username:
                  description:
                      - The Cloud Control API username
                  required: false
                  type: str
            password:
                  description:
                      - The Cloud Control API user password
                  required: false
                  type: str
            api:
                  description:
                      - The Cloud Control API endpoint e.g. api-na.mcp-services.net
                  required: false
                  type: str
            api_version:
                  description:
                      - The Cloud Control API version e.g. 2.11
                  required: false
                  type: str
    region:
        description:
            - The geographical region
        required: false
        default: na
        type: str
    datacenter:
        description:
            - The datacenter name
        required: true
        type: str
    network_domain:
        description:
            - The name of the Cloud Network Domain
        required: false
        type: str
    vlan:
        description:
            - The name of the vlan in which the server is housed
            - Not used for create
        required: false
        type: str
    name:
        description:
            - The name of the server
        required: false
        type: str
    id:
        description:
            - The UUID of the server
        required: false
        type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests
    - configparser
    - pyOpenSSL
    - netaddr
'''

EXAMPLES = '''
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: List all servers
    server_info:
      region: na
      datacenter: NA9
      network_domain: xxxx

  - name: Get a server
    server_info:
      region: na
      datacenter: NA9
      network_domain: xxxx
      name: APITEST
'''

RETURN = '''
data:
    description: dict of returned Objects
    type: complex
    returned: success
    contains:
        count:
            description: The number of objects returned in the list
            returned: success
            type: int
            sample: 1
        server:
            description: List of server objects
            returned: success
            type: complex
            contains:
                started:
                    description: Is the server running
                    type: bool
                guest:
                    description: Information about the guest OS
                    type: complex
                    contains:
                        osCustomization:
                            description: Does the image support guest OS customization
                            type: bool
                        vmTools:
                            description: VMWare Tools information
                            type: complex
                            contains:
                                type:
                                    description: VMWare Tools or Open VM Tools
                                    type: str
                                    sample: VMWARE_TOOLS
                                runningStatus:
                                    description: Is VMWare Tools running
                                    type: str
                                    sample: NOT_RUNNING
                                apiVersion:
                                    description: The version of VMWare Tools
                                    type: int
                                    sample: 9256
                                versionStatus:
                                    description: Additional information
                                    type: str
                                    sample: NEED_UPGRADE
                        operatingSystem:
                            description: Operating System information
                            type: complex
                            contains:
                                displayName:
                                    description: The OS display name
                                    type: str
                                    sample: CENTOS7/64
                                id:
                                    description: The OS UUID
                                    type: str
                                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                family:
                                    description: The OS family
                                    type: str
                                    sample: UNIX
                                osUnitsGroupId:
                                    description: The OS billing group
                                    type: str
                                    sample: CENTOS
                source:
                    description: The source of the image
                    type: complex
                    contains:
                        type:
                            description: The id type of the image
                            type: str
                            sample: IMAGE_ID
                        value:
                            description: The UUID of the image
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                floppy:
                    description: List of the attached floppy drives
                    type: complex
                    contains:
                        driveNumber:
                            description: The drive number
                            type: int
                            sample: 0
                        state:
                            description: The state of the drive
                            type: str
                            sample: NORMAL
                        id:
                            description: The UUID of the drive
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        key:
                            description: Internal usage
                            type: int
                            sample: 8000
                networkInfo:
                    description: Server network information
                    type: complex
                    contains:
                        networkDomainId:
                            description: The UUID of the Cloud Network Domain the server resides in
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        primaryNic:
                            description: The primary NIC on the server
                            type: complex
                            contains:
                                macAddress:
                                    description: the MAC address
                                    type: str
                                    sample: aa:aa:aa:aa:aa:aa
                                vlanName:
                                    description: The name of the VLAN the server resides in
                                    type: str
                                    sample: my_vlan
                                vlanId:
                                    description: the UUID of the VLAN the server resides in
                                    type: str
                                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                state:
                                    description: The state of the NIC
                                    type: str
                                    sample: NORMAL
                                privateIpv4:
                                    description: The IPv4 address of the server
                                    type: str
                                    sample: 10.0.0.10
                                connected:
                                    description: Is the NIC connected
                                    type: bool
                                key:
                                    description: Internal Usage
                                    type: int
                                    sample: 4000
                                ipv6:
                                    description: The IPv6 address of the server
                                    type: str
                                    sample: "1111:1111:1111:1111:0:0:0:1"
                                networkAdapter:
                                    description: The VMWare NIC type
                                    type: str
                                    sample: VMXNET3
                                id:
                                    description: The UUID of the NIC
                                    type: str
                                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                ideController:
                    description: List of the server's IDE controllers
                    type: complex
                    contains:
                        state:
                            description: The state of the controller
                            type: str
                            sample: NORMAL
                        channel:
                            description: The IDE channel number
                            type: int
                            sample: 0
                        key:
                            description: Internal Usage
                            type: int
                            sample: 200
                        adapterType:
                            description: The type of the controller
                            type: str
                            sample: IDE
                        id:
                            description: The UUID of the controller
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        deviceOrDisk:
                            description: List of the attached devices/disks
                            type: complex
                            contains:
                                device:
                                    description: Device/Disk object
                                    type: complex
                                    contains:
                                        slot:
                                            description: The slot number on the controller used by this device
                                            type: int
                                            sample: 0
                                        state:
                                            description: The state of the device/disk
                                            type: str
                                            sample: NORMAL
                                        type:
                                            description: The type of the device/disk
                                            type: str
                                            sample: CDROM
                                        id:
                                            description: The UUID of the device/disk
                                            type: str
                                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                createTime:
                    description: The creation date of the server
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                datacenterId:
                    description: Datacenter id/location
                    type: str
                    sample: NA9
                scsiController:
                    description: List of the SCSI controllers and disk configuration for the image
                    type: complex
                    contains:
                        adapterType:
                            description: The name of the adapter
                            type: str
                            sample: "LSI_LOGIC_SAS"
                        busNumber:
                            description: The SCSI bus number
                            type: int
                            sample: 1
                        disk:
                            description: List of disks associated with this image
                            type: complex
                            contains:
                                id:
                                    description: The disk id
                                    type: str
                                    sample: "112b7faa-ffff-ffff-ffff-dc273085cbe4"
                                scsiId:
                                    description: The id of the disk on the SCSI controller
                                    type: int
                                    sample: 0
                                sizeGb:
                                    description: The initial size of the disk in GB
                                    type: int
                                    sample: 10
                                speed:
                                    description: The disk speed
                                    type: str
                                    sample: "STANDARD"
                        id:
                            description: The SCSI controller id
                            type: str
                            sample: "112b7faa-ffff-ffff-ffff-dc273085cbe4"
                        key:
                            description: Internal use
                            type: int
                            sample: 1000
                state:
                    description: The state of the server
                    type: str
                    sample: NORMAL
                tag:
                    description: List of informational tags associated with the server
                    type: complex
                    contains:
                        value:
                            description: The tag value
                            type: str
                            sample: my_tag_value
                        tagKeyName:
                            description: The tag name
                            type: str
                            sample: my_tag
                        tagKeyId:
                            description: the UUID of the tag
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                virtualHardware:
                    description: Information on the virtual hardware of the server
                    type: complex
                    contains:
                        upToDate:
                            description: Is the VM hardware up to date
                            type: bool
                        version:
                            description: The VM hardware version
                            type: str
                            sample: VMX-10
                memoryGb:
                    description: Server memory in GB
                    type: int
                    sample: 4
                id:
                    description: The UUID of the server
                    type: str
                    sample:  b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                sataController:
                    description: List of SATA controllers on the server
                    type: list
                    contains:
                        adapterType:
                            description: The name of the adapter
                            type: str
                            sample: "LSI_LOGIC_SAS"
                        busNumber:
                            description: The SCSI bus number
                            type: int
                            sample: 1
                        disk:
                            description: List of disks associated with this image
                            type: complex
                            contains:
                                id:
                                    description: The disk id
                                    type: str
                                    sample: "112b7faa-ffff-ffff-ffff-dc273085cbe4"
                                scsiId:
                                    description: The id of the disk on the SCSI controller
                                    type: int
                                    sample: 0
                                sizeGb:
                                    description: The initial size of the disk in GB
                                    type: int
                                    sample: 10
                                speed:
                                    description: The disk speed
                                    type: str
                                    sample: "STANDARD"
                        id:
                            description: The SCSI controller id
                            type: str
                            sample: "112b7faa-ffff-ffff-ffff-dc273085cbe4"
                        key:
                            description: Internal use
                            type: int
                            sample: 1000
                cpu:
                    description: The default CPU specifications for the image
                    type: complex
                    contains:
                        coresPerSocket:
                            description: The number of cores per CPU socket
                            type: int
                            sample: 1
                        count:
                            description: The number of CPUs
                            type: int
                            sample: 2
                        speed:
                            description: The CPU reservation to be applied
                            type: str
                            sample: "STANDARD"
                deployed:
                    description: Is the server deployed
                    type: bool
                name:
                    description: The name of the server
                    type: str
                    sample: my_server
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function

    :returns: Server Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=False, type='str'),
            vlan=dict(default=None, required=False, type='str'),
            name=dict(required=False, type='str'),
            id=dict(required=False, type='str')
        ),
        supports_check_mode=True
    )

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    return_data = return_object('server')
    name = module.params.get('name')
    server_id = module.params.get('id')
    datacenter = module.params.get('datacenter')
    network_domain_name = module.params.get('network_domain')
    vlan_name = module.params.get('vlan')
    network_domain_id = vlan_id = None

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Could not load the user credentials')

    try:
        client = NTTMCPClient(credentials, module.params.get('region'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=e.msg)

    # Get the CND object based on the supplied name
    try:
        if network_domain_name:
            network_domain = client.get_network_domain_by_name(name=network_domain_name, datacenter=datacenter)
            network_domain_id = network_domain.get('id')
        else:
            network_domain_id = None
        if network_domain_name and not network_domain:
            module.fail_json(msg='Failed to locate the Cloud Network Domain - {0}'.format(network_domain_name))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Failed to locate the Cloud Network Domain - {0}'.format(network_domain_name))

    # Get the VLAN object based on the supplied name
    try:
        if vlan_name:
            vlan = client.get_vlan_by_name(name=vlan_name, datacenter=datacenter, network_domain_id=network_domain_id)
            vlan_id = vlan.get('id')
        else:
            vlan_id = None
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Failed to locate the VLAN - {0}'.format(vlan_name))

    try:
        if server_id:
            server = client.get_server_by_id(server_id=server_id)
            if server:
                return_data['server'].append(server)
        elif name:
            server = client.get_server_by_name(datacenter=datacenter,
                                               network_domain_id=network_domain_id,
                                               name=name)
            if server:
                return_data['server'].append(server)
        else:
            servers = client.list_servers(datacenter, network_domain_id, vlan_id, name)
            return_data['server'] = servers
    except (KeyError, IndexError, AttributeError):
        module.fail_json(msg='Could not find the server - {0} in {1}'.format(name, datacenter))

    return_data['count'] = len(return_data.get('server'))

    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
