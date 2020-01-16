#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, NTT Ltd.
#
# Author: Ken Sinfield <ken.sinfield@cis.ntt.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'NTT Ltd.'
}
DOCUMENTATION = '''
---
module: sec_group_info
short_description: Get and List Security Groups
description:
    - Get and List Security Groups
    - https://docs.mcp-services.net/x/NgMu
version_added: "2.10"
author:
    - Ken Sinfield (@kensinfield)
options:
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
    type:
        description:
            - The type of security group
        required: false
        default: vlan
        type: str
        choices:
            - vlan
            - server
    name:
        description:
            - The name of the Security Group
            - A specific value for type should be used when searching by name
        required: false
        type: str
    id:
        description:
            - The UUID of the Security Group
        required: false
        type: str
    server:
        description:
            - The name of a server to search on
            - A specific value for type should be used when searching by server
        required: false
        type: str
    vlan:
        description:
            - The name of the vlan to search on
        required: false
        type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests>=2.21.0
    - configparser>=3.7.4
'''

EXAMPLES = '''
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: List all Server Security Groups in a Network Domain
    sec_group_info:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      type: server

  - name: List all VLAN Security Groups in a Network Domain
    sec_group_info:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      type: vlan

  - name: Get a specific VLAN Security Group by Security Group name
    sec_group_info:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      type: vlan
      name: my_vlan_security_group

  - name: Get a specific Server Security Group by Security Group UUID
    sec_group_info:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      type: server
      id: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae

  - name: Get all Server Security Groups for a specific server
    sec_group_info:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      type: server
      server: my_server
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
        security_group:
            description: List of Security Group objects
            type: complex
            contains:
                name:
                    description: The name of the Security Group
                    type: str
                    sample: my_vlan_security_group
                nics:
                    description: List of NICs associated with the Security Group
                    returned: type == vlan and at least 1 NIC is configured in this group
                    type: complex
                    contains:
                        nic:
                            description: List of NICs in this Security Group
                            type: list
                            contains:
                                ipv4Address:
                                    description: The IPv4 address of the NIC
                                    type: str
                                    sample: 10.0.0.7
                                server:
                                    description: dict containing server information for this NIC
                                    type: complex
                                    contains:
                                        id:
                                            description: The UUID of the server
                                            type: str
                                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                        name:
                                            description: The name of the server
                                            type: str
                                            sample: myServer03
                                id:
                                    description: The UUID of the NIC
                                    type: str
                                    sample: 7b664273-05fa-467f-82c2-6dea32cdf233
                                ipv6Address:
                                    description: The IPv6 address of the NIC
                                    type: str
                                    sample: 1111:1111:1111:1111:0:0:0:1
                                primary:
                                    description: Is the NIC the primary NIC on the server
                                    type: bool
                        vlanId:
                            description: The UUID of the VLAN for the NICs
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                servers:
                    description: List of servers associated with the Security Group
                    returned: type == server and at least 1 server is configured in this group
                    type: complex
                    contains:
                        networkDomainId:
                            description: The UUID of the Cloud Network Domain
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        server:
                            description: List of server objects
                            type: list
                            contains:
                                id:
                                    description: The UUID of the server
                                    type: str
                                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                name:
                                    description: The name of the server
                                    type: str
                                    sample: myServer01
                createTime:
                    description: The time (in zulu) that the Security Group was created
                    type: str
                    sample: "2019-11-26T19:29:52.000Z"
                datacenterId:
                    description: The MCP/datacenter ID
                    type: str
                    sample: NA12
                state:
                    description: The operational state
                    type: str
                    sample: NORMAL
                type:
                    description: The Security Group type
                    type: str
                    sample: VLAN
                id:
                    description: The UUID of the Security Group
                    type: str
                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                description:
                    description: Text description
                    type: str
                    sample: My VLAN security group
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: Server Anti-Affinity Group information
    """
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            type=dict(default='vlan', required=False, choices=['vlan', 'server']),
            name=dict(default=None, required=False, type='str'),
            id=dict(default=None, required=False, type='str'),
            server=dict(default=None, required=False, type='str'),
            vlan=dict(default=None, required=False, type='str')
        ),
        supports_check_mode=True
    )
    network_domain_name = module.params.get('network_domain')
    network_domain_id = None
    server = vlan = dict()
    datacenter = module.params.get('datacenter')
    return_data = return_object('security_group')
    try:
        credentials = get_credentials(module)
        if credentials is False:
            module.fail_json(msg='Could not load the user credentials')
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    try:
        client = NTTMCPClient(credentials, module.params.get('region'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=e.msg)

    # Get the CND
    try:
        network = client.get_network_domain_by_name(network_domain_name, datacenter)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(network_domain_name))

    # If a server name was provided get the server object
    if module.params.get('server'):
        try:
            server = client.get_server_by_name(datacenter=datacenter,
                                               network_domain_id=network_domain_id,
                                               name=module.params.get('server'))
            if not server:
                module.fail_json(msg='Could not find the server - {0} in {1}'.format(module.params.get('server'),
                                                                                     datacenter))
        except (KeyError, IndexError, AttributeError):
            module.fail_json(msg='Could not find the server - {0} in {1}'.format(module.params.get('server'),
                                                                                 datacenter))

    # If a vlan name was provided get the vlan object
    if module.params.get('vlan'):
        try:
            vlan = client.get_vlan_by_name(datacenter=datacenter,
                                           network_domain_id=network_domain_id,
                                           name=module.params.get('vlan'))
            if not vlan:
                module.fail_json(msg='Could not find the VLAN - {0} in {1}'.format(module.params.get('vlan'),
                                                                                   datacenter))
        except (KeyError, IndexError, AttributeError):
            module.fail_json(msg='Could not find the VLAN - {0} in {1}'.format(module.params.get('vlan'),
                                                                               datacenter))

    try:
        if module.params.get('id'):
            return_data['security_group'] = client.get_security_group_by_id(group_id=module.params.get('id'))
        else:
            return_data['security_group'] = client.list_security_groups(network_domain_id=network_domain_id,
                                                                        name=module.params.get('name'),
                                                                        group_type=module.params.get('type'),
                                                                        server_id=server.get('id', None),
                                                                        vlan_id=vlan.get('id', None))
        return_data['count'] = len(return_data['security_group'])
        module.exit_json(data=return_data)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve any Security Groups - {0}'.format(e))


if __name__ == '__main__':
    main()
