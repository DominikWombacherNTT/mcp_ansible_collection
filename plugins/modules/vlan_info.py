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
module: vlan_info
short_description: Get and List VLANs
description:
    - Get and List VLANs
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
            - The datacenter name e.g NA9
        required: true
        type: str
    network_domain:
        description:
            - The name of the Cloud Network Domain
        required: true
        type: str
    name:
        description:
            - The name of the VLAN. If a name is not provided the module will return a list of all VLANs in the network_domain
        required: false
        type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests
    - configparser
    - pyOpenSSL
    - netaddr
        - configparser>=3.7.4
'''

EXAMPLES = '''
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: Get a specific VLAN
    vlan_info:
      region: na
      datacenter: NA9
      network_domain: myCND
      vlan: myVLAN

  - name: List all VLANs
    vlan_info:
      region: na
      datacenter: NA9
      network_domain: myCND
'''

RETURN = '''
data:
    description: dict of returned Objects
    returned: success
    type: complex
    contains:
        count:
            description: The number of objects returned
            returned: success
            type: int
            sample: 1
        vlan:
            description: Dictionary of the vlan
            returned: success
            type: complex
            contains:
                id:
                    description: VLAN ID
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                name:
                    description: VLAN name
                    type: str
                    sample: "My network"
                description:
                    description: VLAN description
                    type: str
                    sample: "My description"
                datacenterId:
                    description: Datacenter id/location
                    type: str
                    sample: NA9
                state:
                    description: Status of the VLAN
                    type: str
                    sample: NORMAL
                attached:
                    description: Whether or not the VLAN is a dettached VLAN
                    type: bool
                createTime:
                    description: The creation date of the VLAN
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                gatewayAddressing:
                    description: Use low (.1) or high (.254) addressing for the default gateway
                    type: str
                    sample: LOW
                ipv4GatewayAddress:
                    description: The IPv4 default gateway for this VLAN
                    type: str
                    sample: "10.0.0.1"
                ipv6GatewayAddress:
                    description: The IPv6 default gateway for this VLAN
                    type: str
                    sample: "1111:1111:1111:1111:0:0:0:1"
                ipv6Range:
                    description: The IPv6 address range
                    type: complex
                    contains:
                        address:
                            description: The base IPv6 network address
                            type: str
                            sample: "1111:1111:1111:1111:0:0:0:0"
                        prefixSize:
                            description: The IPv6 network prefix size
                            type: int
                            sample: 64
                networkDomain:
                    description: The Cloud Network Domain
                    type: complex
                    contains:
                        id:
                            description: The UUID of the Cloud Network Domain of the VLAN
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the Cloud Network Domain
                            type: str
                            sample: "my_network_domain"
                privateIpv4Range:
                    description: The IPv4 address range
                    type: complex
                    contains:
                        address:
                            description: The base IPv46 network address
                            type: str
                            sample: "10.0.0.0"
                        prefixSize:
                            description: The IPv6 network prefix size
                            type: int
                            sample: 24
                small:
                    description: Internal use
                    type: bool
'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: VLAN Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            name=dict(required=False, type='str')
        ),
        supports_check_mode=True
    )

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    return_data = return_object('vlan')
    name = module.params.get('name')
    datacenter = module.params.get('datacenter')
    network_domain_name = module.params.get('network_domain')

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

    # Get the CND
    try:
        network = client.get_network_domain_by_name(name=network_domain_name, datacenter=datacenter)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(network_domain_name))

    # Get a list of existing VLANs and check if the new name already exists
    try:
        vlans = client.list_vlans(datacenter=datacenter, network_domain_id=network_domain_id)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Failed to get a list of VLANs - {0}'.format(exc))
    try:
        if name:
            return_data['vlan'] = [x for x in vlans if x.get('name') == name]
        else:
            return_data['vlan'] = vlans
    except (KeyError, IndexError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the VLAN - {0} in {1}'.format(name, datacenter))

    return_data['count'] = len(return_data.get('vlan'))

    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
