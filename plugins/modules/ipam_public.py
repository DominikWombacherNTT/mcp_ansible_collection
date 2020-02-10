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
module: ipam_public
short_description: IP Address Management
description:
    - IP Address Management
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
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        type: str
    next_free_public_ipv4:
        description:
            - Return the next available public IPv4 address
            - If all existing /31 public IPv4 blocks are used, a new /31 will be provisioned
            - If a new /31 is required this should be set to false
        required: false
        type: bool
        default: true
    ip_address:
        description:
            - Any of the IPv4 addresses within the /31 public IPv4 block
            - Only used for deleting a /31 public IPv4 block
        required: false
        type: str
    id:
        description:
            - The UUID of the /31 public IPv4 block
            - Only used for deleting a /31 public IPv4 block
        required: false
        type: str
    state:
        description:
            - The action to be performed
        required: false
        type: str
        default: present
        choices:
            - present
            - absent
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

  - name: Get the next free public IPv4 address
    ipam_public:
      region: na
      datacenter: NA12
      network_domain: myCND
      state: present

  - name: Allocate a new /31 block
    ipam_public:
      region: na
      datacenter: NA12
      network_domain: myCND
      next_free_public_ipv4: False
      state: present

  - name: Delete a public IPv4 block by IP address
    ipam_public:
      region: na
      datacenter: NA12
      network_domain: myCND
      ip_address: x.x.x.x
      state: absent

  - name: Delete a public IPv4 block by UUID
    ipam_public:
      region: na
      datacenter: NA12
      network_domain: myCND
      id: ffffffff-fff-ffff-ffff-ffffffffffff
      state: absent
'''

RETURN = '''
data:
    description: IP address object
    returned: success
    type: complex
    contains:
        ip:
            description: The Public IPv4  address
            type: str
            returned: when next_free_public_ipv4 == True (Default)
            sample: 10.0.0.10
        block:
            description: List of Public IPv4 addresses within the new block
            type: list
            returned: when next_free_public_ipv4 == False
            sample:
              - 10.0.0.10
        id:
            description: UUID of the public IPv4 block if allocating public IPv4
            type: str
            returned: when next_free_public_ipv4 == False
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object, IP_TO_INT, INT_TO_IP
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def get_next_free_public_ipv4(module, client, network_domain_id):
    """
    Get the next available public IPv4 address.
    If no existing IPv4 blocks exist one will allocated as part of this process

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :returns: The allocated public IPv4 address
    """
    return_data = return_object('ipam')
    return_data['ipam'] = {}
    try:
        result = client.get_next_public_ipv4(network_domain_id)
        return_data['ipam']['ip'] = result.get('ipAddress')
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could get the next free public IPv4 address - {0}'.format(e))

    module.exit_json(changed=result.get('changed'), data=return_data.get('ipam'))


def add_public_ipv4(module, client, network_domain_id):
    """
    Add a new /31 public IPv4 block to the cloud network domain

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :returns: The allocated public IPv4 /31 address space
    """
    return_data = return_object('ipam')
    return_data['ipam'] = {}
    return_data['ipam']['block'] = []
    try:
        public_block_id = client.add_public_ipv4(network_domain_id)
        public_block = client.get_public_ipv4(public_block_id)
        return_data['ipam']['id'] = public_block_id
        for i in range(public_block.get('size')):
            return_data['ipam']['block'].append(INT_TO_IP(IP_TO_INT(public_block.get('baseIp')) + i))
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not add a public IPv4 block - {0}'.format(e))
    except (KeyError, IndexError, AttributeError) as e:
        module.fail_json(msg='Network Domain is invalid or an API failure occurred - {0}'.format(e))

    module.exit_json(changed=True, data=return_data['ipam'])


def delete_public_ipv4(module, client, network_domain_id):
    """
    Delete a /31 public IP address block

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :returns: A message
    """
    ip_address = module.params.get('ip_address')
    public_ipv4_block_id = module.params.get('id')
    if public_ipv4_block_id is None and ip_address is None:
        module.fail_json(msg='A value for id or ip_address is required')
    try:
        if public_ipv4_block_id is None:
            public_ipv4_block = client.get_public_ipv4_by_ip(network_domain_id, ip_address)
            public_ipv4_block_id = public_ipv4_block.get('id')
        else:
            public_ipv4_block = client.get_public_ipv4(public_ipv4_block_id)
        # If the public IPv4 block can't be found then just exit - don't error that is just harsh
        # and not the behaviour we're after.
        if not public_ipv4_block:
            module.exit_json(msg='No matching public IPv4 block exists')
        # However if the public IPv4 block is being used by some NAT or VIP then error
        if client.check_public_block_in_use(network_domain_id, public_ipv4_block.get('baseIp')):
            module.fail_json(msg='The public IPv4 block with ID {0} is in use.'.format(public_ipv4_block_id))
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='The public IPv4 address block ID {0} with IPs '
                                 '{1} and {2} will be removed'.format(
                                     public_ipv4_block_id,
                                     public_ipv4_block.get('baseIp'),
                                     INT_TO_IP(IP_TO_INT(public_ipv4_block.get('baseIp')) + 1)
                                 ))
        client.remove_public_ipv4(public_ipv4_block_id)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not delete the public IPv4 block - {0}'.format(e))

    module.exit_json(changed=True, msg='Successfully deleted the public IPv4 block')


def main():
    """
    Main function

    :returns: Public IPv4 address information
    """
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            next_free_public_ipv4=dict(required=False, default=True, type='bool'),
            ip_address=dict(required=False, default=None, type='str'),
            id=dict(default=None, type='str'),
            state=dict(default='present', choices=['present', 'absent'])
        ),
        supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    network_domain_name = module.params.get('network_domain')
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
    next_free_public_ipv4 = module.params.get('next_free_public_ipv4')

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTMCPClient(credentials, module.params.get('region'))

    # Get the CND
    try:
        network = client.get_network_domain_by_name(name=network_domain_name, datacenter=datacenter)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(network_domain_name))

    if state == 'present' and next_free_public_ipv4:
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='A public IPv4 address will be consumed in '
                                 'the Network Domains with ID {0}'.format(network_domain_id))
        get_next_free_public_ipv4(module, client, network_domain_id)
    elif state == 'present' and not next_free_public_ipv4:
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='A new /31 public IPv4 block will be added to'
                                 ' the Network Domains with ID {0}'.format(network_domain_id))
        add_public_ipv4(module, client, network_domain_id)
    elif state == 'absent':
        delete_public_ipv4(module, client, network_domain_id)


if __name__ == '__main__':
    main()
