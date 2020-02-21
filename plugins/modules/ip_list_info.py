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
module: ip_list_info
short_description: List and Get IP Address Lists
description:
    - List and Get IP Address Lists
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
        type: str
        default: na
    datacenter:
        description:
            - The datacenter name
        required: true
        type: str
    name:
        description:
            - The name of the IP Address List
        required: false
        type: str
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        type: str
    version:
        description:
            - The IP version for the IP Address List(s)
        required: false
        type: str
        default: IPV4
        choices:
            - IPV4
            - IPV6
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

  - name: List all IP address lists for a Cloud Network Domain
    ip_list_info:
      region: na
      datacenter: NA12
      network_domain: myCND

  - name: Get a specific IP address list by IP version (IPv6)
    ip_list_info:
      region: na
      datacenter: NA12
      network_domain: myCND
      version: IPV6

  - name: Get a specific IP address by name
    ip_list_info:
      region: na
      datacenter: NA12
      network_domain: myCND
      name: myIpAddressList
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
            sample: 1
        port_list:
            description: a list of IP Address List objects or strs
            returned: success
            type: complex
            contains:
                id:
                    description: IP Address List UUID
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                description:
                    description: IP Address List description
                    type: str
                    sample: "My IP Address List description"
                name:
                    description: IP Address List name
                    type: str
                    sample: "My IP Address List"
                createTime:
                    description: The creation date of the image
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                state:
                    description: Status of the VLAN
                    type: str
                    sample: NORMAL
                ipVersion:
                    description: The IP version for the IP Address List
                    type: str
                    sample: "IPV6"
                ipAddress:
                    description: List of IP Addresses and/or IP Address Lists
                    type: complex
                    contains:
                        begin:
                            description: The starting IP Address number for this IP Address or range (IPv4 or IPv6)
                            type: int
                            sample: x.x.x.x
                        end:
                            description: The end IP Address number for this range. This is not present for single IP Addresses (IPv4 or IPv6)
                            type: int
                            sample: x.x.x.x
                        prefixSize:
                            description: The prefix size for a given subnet
                            type: str
                            sample: "24"
                childIpAddressList:
                    description: List of child IP Address Lists
                    type: complex
                    contains:
                        id:
                            description: The ID of the IP Address List
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the IP Address List
                            type: str
                            sample: "My Child IP Address List"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: IP Address List Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
            version=dict(required=False, default='IPV4', type='str', choices=['IPV4', 'IPV6']),
            network_domain=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    name = module.params.get('name')
    network_domain_name = module.params.get('network_domain')
    datacenter = module.params.get('datacenter')
    version = module.params.get('version')
    return_data = return_object('ip_list')

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

    try:
        if name:
            result = client.get_ip_list_by_name(network_domain_id, name, version)
            if result:
                return_data['ip_list'].append(result)
        else:
            return_data['ip_list'] = client.list_ip_list(network_domain_id, version)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve a list of the IP Address Lists - {0}'.format(e))

    return_data['count'] = len(return_data.get('ip_list'))
    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
