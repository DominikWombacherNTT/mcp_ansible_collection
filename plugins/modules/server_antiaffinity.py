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
module: server_antiaffinity
short_description: Create, Update and Delete server Anti-Affinity Groups
description:
    - Create, Update and Delete server Anti-Affinity Groups
    - Currently servers can only belong to a single Anti-Affinity Group
    - https://docs.mcp-services.net/x/YgIu
version_added: "2.10.0"
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
    servers:
        description:
            - List of server names to search for
        required: true
        type: list
    state:
        description:
            - The action to be performed
        required: false
        default: present
        choices:
            - present
            - absent
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

  - name: Create a Anti-Affinity Group
    server_antiaffinity:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      servers:
        - my_server_01
        - my_server_02

  - name: Delete a Anti-Affinity Group
    server_antiaffinity:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      servers:
        - my_server_01
        - my_server_02
      state: absent
'''
RETURN = '''
msg:
    description: Status message
    returned: state == absent or failure
    type: str
    sample: The server anti-affinity group already exists
data:
    description: dict of returned Objects
    returned: state == present and success
    type: complex
    contains:
        count:
            description: The number of objects returned
            returned: success
            type: int
            sample: 1
        antiaffinity:
            description: List of the Anti-Affinity Groups
            returned: success
            type: list
            contains:
                id:
                    description: Anti-Affinity Group ID
                    type: str
                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                datacenterId:
                    description: Datacenter ID/location
                    type: str
                    sample: NA9
                createTime:
                    description: The creation date of the Anti-Affinity Group
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                state:
                    description: Status of the Anti-Affinity Group
                    type: str
                    sample: NORMAL
                server:
                    description: List of server objects in the Anti-Affinity Group
                    type: list
                    contains:
                        id:
                            description: Server ID
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        name:
                            description: Server name
                            type: str
                            sample: my_server_01
                        networkInfo:
                            description: Server network information
                            type: complex
                            contains:
                                networkDomainId:
                                    description: The UUID of the Cloud Network Domain for this server
                                    type: str
                                    sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                networkDomainName:
                                    description: The name of the Cloud Network Domain for this server
                                    type: str
                                    sample: my_cnd
                                primary_nic:
                                    description: Information in the primary NIC for this server
                                    type: complex
                                    contains:
                                        ipv6:
                                            description: The IPv6 address of the NIC
                                            type: str
                                            sample: fc00::100
                                        macAddress:
                                            description: The MAC address of the NIC
                                            type: str
                                            sample: aa:aa:aa:aa:aa:aa
                                        privateIpv4:
                                            description: The IPv4 address of the NIC
                                            type: str
                                            sample: 10.0.0.100
                                        vlanId:
                                            description: The UUID of the VLAN for the NIC
                                            type: str
                                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                                        vlanName:
                                            description: The name of the VLAN for the NIC
                                            type: str
                                            sample: my_vlan
'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: Server Anti-Affinity Group information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            servers=dict(required=True, type='list', elements='str'),
            state=dict(default='present', required=False, choices=['present', 'absent'])
        ),
        supports_check_mode=True
    )
    network_domain_name = module.params.get('network_domain')
    network_domain_id = aa_group = None
    server_ids = list()
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

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
        network = client.get_network_domain_by_name(network_domain_name, datacenter)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(network_domain_name))

    # Get the servers
    for server in module.params.get('servers'):
        try:
            server = client.get_server_by_name(datacenter=datacenter,
                                               network_domain_id=network_domain_id,
                                               name=server)
            if server:
                server_ids.append(server.get('id'))
            else:
                module.fail_json(msg='Could not find the server - {0} in {1}'.format(server, datacenter))
        except (KeyError, IndexError, AttributeError):
            module.fail_json(msg='Could not find the server - {0} in {1}'.format(server, datacenter))

    # Attempt to find any existing AntiAffinity Group for this server combination
    try:
        aa_group = client.get_anti_affinity_group_by_servers(server_ids[0], server_ids[1])
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve any Server Anti Affinity Groups - {0}'.format(e))

    try:
        if state == 'present':
            if aa_group:
                module.exit_json(msg='The server anti-affinity group already exists', data=aa_group)
            if module.check_mode:
                module.exit_json(msg='A new server anti-affinity group will be created')
            client.create_anti_affinity_group(server_ids[0], server_ids[1])
            aa_group = client.get_anti_affinity_group_by_servers(server_ids[0], server_ids[1])
            module.exit_json(changed=True, data=aa_group)
        elif state == 'absent':
            if not aa_group:
                module.exit_json(msg='No server anti-affinity group exists for this server combination')
            if module.check_mode:
                module.exit_json(msg='The server anti-affinity group {0} will be removed'.format(aa_group.get('id')))
            client.delete_anti_affinity_group(aa_group.get('id'))
            module.exit_json(changed=True, msg='The Anti-Affinity Group {0} was successfully removed'.format(aa_group.get('id')))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='{0}'.format(e).replace('"', '\''))


if __name__ == '__main__':
    main()
