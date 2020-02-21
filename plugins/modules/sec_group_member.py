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
module: sec_group_member
short_description: Add Server or NICs to a Security Group
description:
    - Create, Add Server or NICs to a Security Group
    - https://docs.mcp-services.net/x/NgMu
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
        required: true
        type: str
    vlan:
        description:
            - The name of the vlan to search on
        required: false
        type: str
    state:
        description:
            - The action to be performed
            - Unless force is set to True a Security Group can only be removed once there are no member servers
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

  - name: Add a server to a Security Group
    sec_group:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      name: my_sec_group
      server: my_server_01

  - name: Add a NIC to a Security Group
    sec_group:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      name: my_vlan_sec_group
      server: my_server_01
      vlan: vlan_01

  - name: Remove a NIC from Security Group by name
    sec_group:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      name: my_vlan_sec_group
      server: my_server_01
      vlan: vlan_01
      state: absent

  - name: Remove a NIC from Security Group by ID
    sec_group:
      region: na
      datacenter: NA9
      network_domain: my_cnd
      name: my_vlan_sec_group
      id: 7b664273-05fa-467f-82c2-6dea32cdf233
      state: absent
'''
RETURN = '''
msg:
    description: A helpful message
    returned: state == absent and on failure
    type: str
    sample: "The Security Group was successfully removed"
data:
    description: Security Group object
    returned: state == present
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
                    description: NIC object
                    type: list
                    contains:
                        ipv4Address:
                            description: The IPv4 address of the NIC
                            type: str
                            sample: 10.0.0.7
                        server:
                            description: dict containing server information for this NIC
                            type: str
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

from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, compare_json
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def create_security_group(module, client, network_domain_id=None, vlan_id=None):
    """
    Create a Security Group

    :arg module: The Ansible module
    :arg client: The CC API client instance
    :kw network_domain_id: The UUID of the Cloud Network Domain
    :kw vlan_id: The UUID of a VLAN
    :returns: The updated Security Group
    """
    sec_group = None
    if not module.params.get('name'):
        module.fail_json(msg='A name is required when creating a Security Group')
    try:
        result = client.create_security_group(network_domain_id=network_domain_id,
                                              vlan_id=vlan_id,
                                              name=module.params.get('name'),
                                              description=module.params.get('description'))
        sec_group = client.get_security_group_by_id(group_id=result)
        if not sec_group:
            module.warn(warning='Could not verify the creation of the Security Group with ID {0}'.format(result))
        return sec_group
    except (KeyError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not create the Security Group - {0}'.format(e))


def update_security_group(module, client, sec_group):
    """
    Update a Security Group
    :arg module: The Ansible module
    :arg client: The CC API client instance
    :arg sec_group: The exitsting Security Group to be updated
    :returns: The updated Security Group
    """
    try:
        result = client.update_security_group(group_id=sec_group.get('id'),
                                              name=module.params.get('new_name'),
                                              description=module.params.get('description'))
        sec_group = client.get_security_group_by_id(group_id=sec_group.get('id'))
        if not sec_group:
            module.warn(warning='Could not verify the update of the Security Group with ID {0}'.format(result))
        return sec_group
    except (KeyError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not update the Security Group - {0}'.format(e))


def delete_security_group_members(module, client, sec_group, group_type):
    """
    Delete all members of a Security Group
    :arg module: The Ansible module
    :arg client: The CC API client instance
    :arg sec_group: The Security Group object

    :returns: True
    """
    changed = False
    member_list = list()
    try:
        if group_type == 'server':
            member_list = sec_group.get('servers', dict()).get('server', list())
        elif group_type == 'vlan':
            member_list = sec_group.get('nics', dict()).get('nic', list())
        for member in member_list:
            result = client.delete_security_group_member(sec_group.get('id'),
                                                         member.get('id'),
                                                         group_type)
            if result.get('responseCode') != 'OK':
                module.fail_json(changed=changed,
                                 msg='Could not remove the member {0} - {1}'.format(member.get('id'),
                                                                                    result.get('content')))
            changed = True
    except (AttributeError, IndexError, KeyError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not remove all Security Group members - {0}'.format(e))
    return True


def compare_security_group(module, sec_group):
    """
    Compare an existing Security Group to one using the supplied arguments

    :arg module: The Ansible module instance
    :arg vlan: The existing VLAN object
    :returns: the comparison result
    """
    new_sec_group = deepcopy(sec_group)
    if module.params.get('new_name'):
        new_sec_group['name'] = module.params.get('new_name')
    if module.params.get('description'):
        new_sec_group['description'] = module.params.get('description')

    compare_result = compare_json(new_sec_group, sec_group, None)
    # Implement Check Mode
    if module.check_mode:
        module.exit_json(data=compare_result)
    return compare_result.get('changes')


def main():
    """
    Main function
    :returns: Server Anti-Affinity Group information or a message
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            id=dict(default=None, required=False, type='str'),
            name=dict(default=None, required=False, type='str'),
            server=dict(required=True, type='str'),
            vlan=dict(default=None, required=False, type='str'),
            state=dict(default='present', required=False, choices=['present', 'absent'])
        ),
        supports_check_mode=True
    )
    network_domain_name = module.params.get('network_domain')
    network_domain_id = group_type = member_id = None
    vlan = sec_group = server = nic = dict()
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
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

    # Try and find any existing Security Group
    try:
        if module.params.get('name'):
            sec_groups = client.list_security_groups(network_domain_id=None if module.params.get('vlan') else network_domain_id,
                                                     name=None,
                                                     group_type=None,
                                                     server_id=None,
                                                     vlan_id=vlan.get('id', None))
            sec_group = [x for x in sec_groups if x.get('name') == module.params.get('name')][0]
        if module.params.get('id'):
            sec_group = client.get_security_group_by_id(group_id=module.params.get('id'))
        if sec_group:
            group_type = sec_group.get('type').lower()
        else:
            module.fail_json(msg='Could not find the Security Group {0}'.format(module.params.get('name')))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Could not find the Security Group {0}'.format(module.params.get('name')))

    # Check if the Server exists based on the supplied name
    try:
        server = client.get_server_by_name(datacenter, network_domain_id, None, module.params.get('server'))
        if not server:
            module.fail_json(msg='Failed to find the server - {0}'.format(module.params.get('server')))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed to find the server - {0}'.format(e))

    # Search for any NICs that match any supplied VLAN
    if module.params.get('vlan'):
        try:
            nics = [server.get('networkInfo', {}).get('primaryNic')] + server.get('networkInfo', {}).get('additionalNic')
            nic = [x for x in nics if x.get('vlanName') == module.params.get('vlan')][0]
        except (KeyError, IndexError, AttributeError):
            module.fail_json(msg='Failed to find the NIC for server {0} in VLAN {1}'.format(module.params.get('server'),
                                                                                            module.params.get('vlan')))

        # Check if the NIC already exists in the Security Group
        try:
            if [x for x in sec_group.get('nics', {}).get('nic', []) if x.get('id') == nic.get('id')][0]:
                if state == 'present':
                    module.exit_json(msg='NIC with ID {0} is already a member of the Security Group {1}'.format(
                        nic.get('id'),
                        sec_group.get('id')))
        except IndexError:
            if state == 'absent':
                module.exit_json(msg='The NIC with ID {0} is not a member of the Security Group {1}'.format(
                    nic.get('id'),
                    sec_group.get('id')))
            pass

        if module.check_mode:
            module.exit_json(msg='The NIC ID {0} will be added to the Security Group with ID {1}'.format(
                nic.get('id'),
                sec_group.get('id')))
        member_id = nic.get('id')
    else:
        member_id = server.get('id')
        # Check if the server is already a member of the Security Group
        try:
            if [x for x in sec_group.get('servers', {}).get('server', []) if x.get('id') == server.get('id')][0]:
                if state == 'present':
                    module.exit_json(msg='Server with ID {0} is already a member of the Security Group {1}'.format(
                        server.get('id'),
                        sec_group.get('id')))
        except IndexError:
            if state == 'absent':
                module.exit_json(msg='The Server with ID {0} is not a member of the Security Group {1}'.format(
                    server.get('id'),
                    sec_group.get('id')))
            pass

        if module.check_mode:
            module.exit_json(msg='The Server ID {0} will be added to the Security Group with ID {1}'.format(
                server.get('id'),
                sec_group.get('id')))

    try:
        if state == 'present':
            try:
                client.add_security_group_member(group_id=sec_group.get('id'),
                                                 group_type=group_type,
                                                 member_id=member_id)
                sec_group = client.get_security_group_by_id(group_id=sec_group.get('id'))
                if not sec_group:
                    module.warn(warning='Could not verify the update of the Security Group with ID {0}'.format(sec_group.get('id')))
                module.exit_json(changed=True, data=sec_group)
            except (NTTMCPAPIException) as e:
                module.fail_json(msg='Failed to update the Security Group - {0}'.format(e))
        # Delete the Security Group
        elif state == 'absent':
            if not sec_group:
                module.exit_json(msg='Security Group not found')
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='An existing Security Group was found for {0} and will be removed'.format(
                    sec_group.get('id')))
            result = client.delete_security_group_member(group_id=sec_group.get('id'),
                                                         member_id=member_id,
                                                         group_type=group_type)
            if result.get('responseCode') == 'OK':
                module.exit_json(changed=True, msg='The Security Group member was successfully removed')
            module.fail_json(msg='Could not remove the Security Group member - {0}'.format(result.content))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not remove the Security Group member - {0}'.format(e))


if __name__ == '__main__':
    main()
