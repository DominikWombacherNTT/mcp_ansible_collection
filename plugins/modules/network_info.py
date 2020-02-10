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
module: network_info
short_description: List, Get Cloud Network Domains (CND)
description:
    - List, Get Cloud Network Domains (CND)
version_added: "2.10"
author:
    - Ken Sinfield (@kensinfield)
options:
    region:
        description:
            - The geographical region
        required: false
        type: str
        default: na
    datacenter:
        description:
            - The datacenter name
        required: true
        type: str
    name:
        description:
            - The name of the Cloud Network Domain
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

  - name: List all Network Domains in a datacenter
    network_info:
      region: na
      datacenter: NA12

  - name: Get a specific Cloud Network Domain
    network_info:
      region: na
      datacenter: NA12
      name: myCND
'''

RETURN = '''
data:
    description: dict of returned Objects
    type: complex
    returned: success
    contains:
        count:
            description: The number of objects returned
            returned: success
            type: int
        network:
            description: Dictionary of the network domain
            returned: success
            type: complex
            contains:
                id:
                    description: Network Domain ID
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                name:
                    description: Network Domain name
                    type: str
                    sample: "My network"
                description:
                    description: Network Domain description
                    type: str
                    sample: "My network description"
                datacenterId:
                    description: Datacenter id/location
                    type: str
                    sample: NA9
                state:
                    description: Status of the Network Domain
                    type: str
                    sample: NORMAL
                createTime:
                    description: The creation date of the image
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                ipv4CpncGatewayAddress:
                    description: The CPNC gateway address (mostly for internal use)
                    type: str
                    sample: "10.10.10.10"
                ipv4InternetGatewayAddress:
                    description: The upstream gateway address
                    type: str
                    sample: "10.10.10.10"
                ipv6CpncGatewayAddress:
                    description: The CPNC gateway address (mostly for internal use)
                    type: str
                    sample: "1111:1111:1111:1111:0:0:0:1"
                ipv6InternetGatewayAddress:
                    description: The upstream gateway address
                    type: str
                    sample: "1111:1111:1111:1111:0:0:0:1"
                outsideTransitVlanIpv4Subnet:
                    description: The upstream IPv4 transit network
                    type: complex
                    contains:
                        address:
                            description: The upstream IPv4 transit network gateway
                            type: str
                            sample: "10.10.10.0"
                        prefixSize:
                            description: The upstream IPv4 transit network prefix
                            type: int
                            sample: 24
                outsideTransitVlanIpv6Subnet:
                    description: The upstream IPv6 transit network
                    type: complex
                    contains:
                        address:
                            description: The upstream IPv6 transit network gateway
                            type: str
                            sample: "1111:1111:1111:1111:0:0:0:0"
                        prefixSize:
                            description: The upstream IPv6 transit network prefix
                            type: int
                            sample: 64
                snatIpv4Address:
                    description: The outgoing public IPv4 source address
                    type: str
                    sample: "1.1.1.1"
                type:
                    description: The VLAN type
                    type: str
                    sample: "ADVANCED"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: Cloud Network Domain Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
        ),
        supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    return_data = return_object('network_domain')
    name = module.params.get('name')
    datacenter = module.params.get('datacenter')

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    try:
        client = NTTMCPClient(credentials, module.params.get('region'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e.msg))

    # Get a list of existing CNDs and check if the name already exists
    try:
        networks = client.list_network_domains(datacenter=datacenter)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Failed to get a list of Cloud Network - {0}'.format(e))
    try:
        if name:
            return_data['network_domain'] = [x for x in networks if x.get('name') == name]
        else:
            return_data['network_domain'] = networks
    except (KeyError, IndexError, AttributeError) as e:
        module.fail_json(msg='Could not find the Cloud Network Domain - {0} in {1}'.format(name, datacenter))

    return_data['count'] = len(return_data['network_domain'])

    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
