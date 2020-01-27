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
module: ansible_gw
short_description: List, Create and Destory an Ansible Bastion Host
description:
    - List, Create and Destory an Ansible Bastion Host
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
    vlan:
        description:
            - The name of the VLAN to create the Bastion Host in
        required: true
        type: str
    name:
        description:
            - The name of the Bastion Host
        required: false
        type: str
        default: ansible_gw
    password:
        description:
            - The root password for the host
        required: false
        type: str
    image:
        description:
            - The name of the Image to use whend creating a new server
            - Must be a Linux based image
            - Use infrastructure -> state=get_image to get a list
            - of that available images
        required: false
        type: str
    ipv4:
        description:
            - The IPv4 address of the host
            - If one is not provided one will be automatically allocated
        required: false
        type: str
    src_ip:
        description:
            - The IPv4 source network/host address to restrict SSH access to the Bastion Host public IPv4 address
        required: false
        type: str
        default: ANY
    src_prefix:
        description:
            - The IPv4 subnet mask to apply to the src_ip address
        required: false
        type: str
    wait:
        description:
            - Wait for the server to complete deployment
        required: false
        type: bool
        default: true
    wait_time:
            description:
                - The maximum time the module will wait for the server to complete deployment in seconds
            required: false
            type: int
            default: 1200
    wait_poll_interval:
            description:
                - How often the module will poll the Cloud Control API to check the status of the Bastion Host deployment in seconds
            required: false
            type: int
            default: 30
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
    - Must have sshpass installed for playbooks to use this module
requirements:
    - requests
    - configparser
    - pyOpenSSL
    - netaddr
'''
EXAMPLES = '''
# Creating an Ansible gateway
- hosts: localhost
  gather_facts: no
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: Deploy an Ansible Gateway
    ansible_gw:
      region: na
      datacenter: NA12
      network_domain: myCND
      vlan: myVLAN
      image: "CentOS 7 64-bit 2 CPU"
      src_ip: x.x.x.x
      state: present

  - name: Delete an Ansible Gateway
    ansible_gw:
      region: na
      datacenter: NA12
      network_domain: myCND
      vlan: myVLAN
      name: ansible_gw
      state: absent

# Full use case (Playbook)
- hosts: localhost
  gather_facts: no
  connection: local
  collections:
    - nttmcp.mcp
  vars:
    # Modify these if you really want
    region: na
    datacenter: NA12
    image: "CentOS 7 64-bit 2 CPU"
    cnd: myCND2
    cnd_description: "My CND2"
    vlan: myVLAN2
    my_host: "12.167.142.34"
    # Do NOT modify these
    ansible_gateway: "ansible_gateway"
  tasks:

  - name: Generate Host Password
    set_fact:
      host_password: "{{lookup('password', './host_passwd_file chars=ascii_letters,.:{}()-_+=')}}"
    tags:
      - testing
      - create

  - name: Show host password
    debug:
      var: host_password
    tags:
      - create

  - local_action: stat path=public_ipv4
    register: public_ipv4_state
    become: no
    tags:
      - testing
      - create
      - delete

  - name: Create the CND
    network:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      name: "{{cnd}}"
      description: "{{cnd_description}}"
      state: present
    tags:
      - testing
      - create
    register: cnd_return

  - name: Create the VLAN
    vlan:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      network_domain: "{{cnd}}"
      name: "{{vlan}}"
      ipv4_network_address: "172.16.0.0"
      ipv4_prefix_size: 24
      state: present
    tags:
      - testing
      - create
    register: vlan_return

  - name: Deploy an Ansible Gateway
    ansible_gw:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      name: "ANSIBLE_TEST"
      network_domain: "{{cnd}}"
      vlan: "{{vlan}}"
      image: "{{image}}"
      src_ip: "{{my_host}}"
      state: present
    tags:
      - testing
      - create
    register: server

  - name: debug
    debug:
      var: server
    tags:
      - create

  - set_fact:
      ansible_pw: "{{server.data.password | default(host_password)}}"
      ansible_gw: "{{server.data.public_ipv4}}"
    tags:
      - testing
      - create

  - set_fact:
      ansible_pw: "{{host_password}}"
    when: server.data.password == None
    tags:
      - testing
      - create

  - debug:
      var: ansible_pw
    tags:
      - testing
      - create

  - name: Add_Host
    add_host:
      name: "{{ansible_gw}}"
    tags:
      - testing
      - create

  - debug:
      var: ansible_gw
    tags:
      - testing
      - create

  - name: Remove an Ansible Gateway
    ansible_gw:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      name: "ANSIBLE_TEST"
      network_domain: "{{cnd}}"
      vlan: "{{vlan}}"
      state: absent
    register: remove_server
    tags:
      - testing
      - delete

  - name: Debug Removal of the Ansible gateway
    debug:
      var: remove_server
    tags:
      - testing
      - delete

  - name: Remove the VLAN
    vlan:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      network_domain: "{{cnd}}"
      name: "{{vlan}}"
      state: absent
    tags:
      - testing
      - delete

  - name: Remove the CND
    network:
      region: "{{region}}"
      datacenter: "{{datacenter}}"
      name: "{{cnd}}"
      state: absent
    tags:
      - testing
      - delete

- hosts: "{{hostvars.localhost.ansible_gw}}"
  gather_facts: no
  environment:
    host_key_checking: False
  vars:
    ansible_user: root
    ansible_gw: "{{hostvars['localhost']['ansible_gw']}}"
    ansible_pw: "{{hostvars['localhost']['ansible_pw']}}"
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    ansible_ssh_pass: "{{ ansible_pw }}"
  tasks:
  - debug:
      var: ansible_pw
    tags:
      - testing
      - create

  - name: Get Hostname
    shell: hostname
    register: hostname
    tags:
      - testing
      - create

  - debug:
      var: hostname
    tags:
      - testing
      - create
'''
RETURN = '''
data:
    description: Object with the Bastion Host details
    type: complex
    returned: when state == present
    contains:
        id:
            description: The UUID of the server
            type: str
            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        password:
            description: The password for the server if generated by the module
            type: str
            sample: "my_password"
        private_ipv4:
            description: The private IPv4 address of the Bastion Host
            type: str
            sample: "10.0.0.10"
        ipv6:
            description: The IPv6 address of the Bastion Host
            type: str
            sample: "1111:1111:1111:1111:0:0:0:1"
        public_ipv4:
            description: The public IPv4 address assigned to the Bastion Host
            type: str
            sample: "x.x.x.x"
'''

import traceback
from time import sleep
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, generate_password
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException

ACL_RULE_NAME = 'Ipv4.Internet.to.Ansible.SSH'


def create_server(module, client, network_domain_id, vlan_id):
    """
    Create the Bastion Host

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain for the Bastion Host
    :arg vlan_id: The UUID of the VLAN for the Bastion Host
    :returns: The Bastion Host server object
    """
    params = {}
    params['networkInfo'] = {}
    params['networkInfo']['primaryNic'] = {}
    datacenter = module.params['datacenter']

    params['networkInfo']['networkDomainId'] = network_domain_id
    params['networkInfo']['primaryNic']['vlanId'] = vlan_id
    if module.params['ipv4']:
        params['networkInfo']['primaryNic']['privateIpv4'] = module.params.get('ipv4')

    image_name = module.params.get('image')
    params['name'] = module.params.get('name')
    params['start'] = True
    ngoc = False

    if module.params.get('password'):
        params['administratorPassword'] = module.params.get('password')
    else:
        params['administratorPassword'] = generate_password()

    try:
        image = client.list_image(datacenter_id=datacenter, image_name=image_name)
        params['imageId'] = image.get('osImage')[0].get('id')
    except (KeyError, IndexError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed to find the  Image {0} - {1}'.format(image_name, e))

    try:
        client.create_server(ngoc, params)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not create the server - {0}'.format(exc), exception=traceback.format_exc())

    wait_result = wait_for_server(module, client, params.get('name'), datacenter, network_domain_id, 'NORMAL', True, False, None)
    if wait_result is None:
        module.fail_json(msg='Could not verify the server creation. Password: {0}'.format(params.get('administratorPassword')))

    wait_result['password'] = params.get('administratorPassword')
    return wait_result


def allocate_public_ip(module, client, network_domain_id):
    """
    Allocate the Public IP to the Bastion Host

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain for the Bastion Host
    """
    return_data = {}
    try:
        return_data['id'] = client.add_public_ipv4(network_domain_id)
        return_data['ip'] = client.get_public_ipv4(return_data['id'])['baseIp']
        return return_data
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not add a public IPv4 block - {0}'.format(exc), exception=traceback.format_exc())
    except KeyError:
        module.fail_json(msg='Network Domain is invalid or an API failure occurred.')


def create_nat_rule(module, client, network_domain_id, internal_ip, external_ip):
    """
    Create the NAT rule for the Bastion Host

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain for the Bastion Host
    :arg internal_ip: The private IPv4 address of the Bastion Host
    :arg external_ip: The public IPv4 address to use
    """
    if internal_ip is None or external_ip is None:
        module.fail_json(msg='Valid internal_ip and external_ip values are required')
    try:
        return client.create_nat_rule(network_domain_id, internal_ip, external_ip)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not create the NAT rule - {0}'.format(exc), exception=traceback.format_exc())
    except KeyError:
        module.fail_json(msg='Network Domain is invalid')


def create_fw_rule(module, client, network_domain_id, public_ipv4):
    """
    Create the firewall rule for the Bastion Host

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain for the Bastion Host
    :arg public_ipv4: The public IPv4 address to use
    """
    src_ip = module.params['src_ip']
    src_prefix = module.params['src_prefix']
    try:
        fw_rule = client.fw_args_to_dict(True,
                                         None,
                                         network_domain_id,
                                         ACL_RULE_NAME,
                                         'ACCEPT_DECISIVELY',
                                         'IPV4',
                                         'TCP',
                                         src_ip,
                                         src_prefix,
                                         None,
                                         public_ipv4,
                                         None,
                                         None,
                                         'ANY',
                                         None,
                                         None,
                                         '22',
                                         None,
                                         None,
                                         True,
                                         'FIRST',
                                         None)
        return client.create_fw_rule(fw_rule)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not create the firewall rule - {0}'.format(exc), exception=traceback.format_exc())


def update_fw_rule(module, client, fw_rule, network_domain_id, public_ipv4):
    """
    Update the firewall rule for the Bastion Host

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg fw_rule: The existing firewall rule
    :arg network_domain_id: The UUID of the CND
    :arg public_ipv4: The public IPv4 address to use
    """
    fw_rule_id = fw_rule.get('id')
    src_ip = module.params.get('src_ip')
    src_prefix = module.params.get('src_prefix')

    try:
        new_fw_rule = client.fw_args_to_dict(False,
                                             fw_rule_id,
                                             network_domain_id,
                                             fw_rule.get('name'),
                                             'ACCEPT_DECISIVELY',
                                             'IPV4',
                                             'TCP',
                                             src_ip,
                                             src_prefix,
                                             None,
                                             public_ipv4,
                                             None,
                                             None,
                                             'ANY',
                                             None,
                                             None,
                                             '22',
                                             None,
                                             None,
                                             True,
                                             'FIRST',
                                             None)
        client.update_fw_rule(new_fw_rule)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not update the firewall rule - {0}'.format(exc), exception=traceback.format_exc())
    except KeyError as exc:
        module.fail_json(changed=False, msg='Invalid data - {0}'.format(exc), exception=traceback.format_exc())


def delete_server(module, client, server):
    """
    Delete a server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain: The server dict
    :returns: A message
    """
    server_exists = True
    name = server.get('name')
    datacenter = server.get('datacenterId')
    network_domain_id = server.get('networkInfo').get('networkDomainId')
    time = 0
    wait_time = module.params.get('wait_time')
    wait_poll_interval = module.params.get('wait_poll_interval')
    wait = module.params.get('wait')

    # Check if the server is running and shut it down
    if server['started']:
        try:
            client.shutdown_server(server_id=server['id'])
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, True, wait_poll_interval)
        except NTTMCPAPIException as e:
            module.fail_json(msg='Could not shutdown the server - {0}'.format(e), exception=traceback.format_exc())

    try:
        client.delete_server(server['id'])
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not delete the server - {0}'.format(e), exception=traceback.format_exc())
    if wait:
        while server_exists and time < wait_time:
            servers = client.list_servers(datacenter=datacenter, network_domain_id=network_domain_id)
            server_exists = [x for x in servers if x['id'] == server['id']]
            sleep(wait_poll_interval)
            time = time + wait_poll_interval

        if server_exists and time >= wait_time:
            module.fail_json(msg='Timeout waiting for the server to be deleted')

    return True


def delete_fw_rule(module, client, network_domain_id, name):
    """
    Delete a firewall rule

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg name: The name of the firewall rule to be removed
    :returns: A message
    """
    try:
        fw_rule = client.get_fw_rule_by_name(network_domain_id, name)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not retrieve a list of firewall rules - {0}'.format(e), exception=traceback.format_exc())
    except KeyError:
        module.fail_json(msg='Network Domain is invalid')

    try:
        client.remove_fw_rule(fw_rule['id'])
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not delete the firewall rule - {0}'.format(e), exception=traceback.format_exc())
    except KeyError:
        module.fail_json(msg='Could not find the firewall rule - {0}'.format(e), exception=traceback.format_exc())

    return True


def delete_nat_rule(module, client, nat_rule_id):
    """
    Delete a NAT rule

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg nat_rule_id: The UUID of the existing NAT rule to delete
    :returns: A message
    """
    if nat_rule_id is None:
        module.fail_json(msg='A value for id is required')
    try:
        client.remove_nat_rule(nat_rule_id)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not delete the NAT rule - {0}'.format(e), exception=traceback.format_exc())

    return True


def delete_public_ipv4(module, client, public_ipv4_block_id):
    """
    Delete a /31 public IP address block

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg public_ipv4_block_id: The UUID of the public IPv4 address block
    :returns: A message
    """
    if public_ipv4_block_id is None:
        module.fail_json(msg='A value for id is required')
    try:
        client.remove_public_ipv4(public_ipv4_block_id)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not delete the public IPv4 block - {0}'.format(e), exception=traceback.format_exc())

    return True


def wait_for_server(module, client, name, datacenter, network_domain_id, state, check_for_start=False,
                    check_for_stop=False, wait_poll_interval=None):
    """
    Wait for the server deployment to complete.

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg datacenter: The MCP ID
    :arg network_domain_id: The UUID of the network domain for the Bastion Host
    :arg state: The state to wait for e.g. NORMAL
    :arg check_for_start: Should we check if the server is started
    :arg check_for_stop: Should we check if the server is stooped
    :arg wait_poll_internal: Optional custom wait polling interval value in seconds
    """
    set_state = False
    actual_state = ''
    start_state = ''
    time = 0
    wait_time = module.params.get('wait_time')
    if wait_poll_interval is None:
        wait_poll_interval = module.params.get('wait_poll_interval')
    server = []
    while not set_state and time < wait_time:
        sleep(wait_poll_interval)
        try:
            server = client.get_server_by_name(datacenter=datacenter, network_domain_id=network_domain_id, name=name)
        except NTTMCPAPIException as exc:
            module.fail_json(msg='Failed to get a list of servers - {0}'.format(exc), exception=traceback.format_exc())
        try:
            actual_state = server.get('state')
            start_state = server.get('started')
        except (KeyError, IndexError, AttributeError):
            module.fail_json(msg='Failed to find the server - {0}'.format(name))
        if actual_state != state or (check_for_start and not start_state) or (check_for_stop and start_state):
            time = time + wait_poll_interval
        else:
            set_state = True

    if server and time >= wait_time:
        module.fail_json(msg='Timeout waiting for the server to be created')

    return server


def main():
    """
    Main function
    :returns: Ansible Gateway Host Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            vlan=dict(required=True, type='str'),
            name=dict(required=False, default='ansible_gw', type='str'),
            password=dict(default=None, required=False, type='str'),
            image=dict(required=False, type='str'),
            ipv4=dict(default=None, required=False, type='str'),
            src_ip=dict(default='ANY', required=False, type='str'),
            src_prefix=dict(default=None, required=False, type='str'),
            state=dict(default='present', choices=['present', 'absent']),
            wait=dict(required=False, default=True, type='bool'),
            wait_time=dict(required=False, default=1200, type='int'),
            wait_poll_interval=dict(required=False, default=30, type='int')
        )
    )

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    name = module.params.get('name')
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
    network_domain_name = module.params.get('network_domain')
    vlan_name = module.params.get('vlan')
    vlan_id = ansible_gw = None
    return_data = {}
    changed = False

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

    client = NTTMCPClient(credentials, module.params['region'])

    # Get the CND object based on the supplied name
    try:
        network = client.get_network_domain_by_name(datacenter=datacenter, name=network_domain_name)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Failed to find the Cloud Network Domain - {0}'.format(exc))

    # Get the VLAN object based on the supplied name
    try:
        vlan = client.get_vlan_by_name(datacenter=datacenter, network_domain_id=network_domain_id, name=vlan_name)
        vlan_id = vlan.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Failed to get a list of VLANs - {0}'.format(exc), exception=traceback.format_exc())

    # Check if the server exists based on the supplied name
    try:
        ansible_gw = client.get_server_by_name(datacenter, network_domain_id, vlan_id, name)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Failed attempting to locate any existing server - {0}'.format(exc))

    # Handle the case where the gateway already exists. This could mean a playbook re-run
    # If the server exists then we need to check:
    #   a public IP is allocated and if not get the next one
    #   the NAT rule is present and correct and if not update/create it
    #   the Firewall rule is present and correct and if not update/create it
    if state == 'present' and ansible_gw:
        try:
            ansible_gw_private_ipv4 = ansible_gw.get('networkInfo').get('primaryNic').get('privateIpv4')
            # Check if the NAT rule exists and if not create it
            nat_result = client.get_nat_by_private_ip(network_domain_id, ansible_gw.get('networkInfo').get('primaryNic').get('privateIpv4'))
            if nat_result:
                public_ipv4 = nat_result.get('externalIp')
            else:
                public_ipv4 = client.get_next_public_ipv4(network_domain_id).get('ipAddress')
                create_nat_rule(module, client, network_domain_id, ansible_gw_private_ipv4, public_ipv4)
                changed = True
            # Check if the Firewall rule exists and if not create it
            fw_result = client.get_fw_rule_by_name(network_domain_id, ACL_RULE_NAME)
            if fw_result:
                update_fw_rule(module, client, fw_result, network_domain_id, public_ipv4)
            else:
                create_fw_rule(module, client, network_domain_id, public_ipv4)
                changed = True
            return_data['server_id'] = ansible_gw.get('id')
            return_data['password'] = ansible_gw.get('password', None)
            return_data['internal_ipv4'] = ansible_gw.get('networkInfo').get('primaryNic').get('privateIpv4')
            return_data['ipv6'] = ansible_gw.get('networkInfo').get('primaryNic').get('ipv6')
            return_data['public_ipv4'] = public_ipv4
            module.exit_json(changed=changed, data=return_data)
        except (KeyError, IndexError, AttributeError) as e:
            module.fail_json(msg='Could not ascertain the current server state: {0}'.format(e))
    elif state == 'present' and not ansible_gw:
        try:
            ansible_gw = create_server(module, client, network_domain_id, vlan_id)
            changed = True
            ansible_gw_private_ipv4 = ansible_gw.get('networkInfo').get('primaryNic').get('privateIpv4')
            # Check if the NAT rule exists and if not create it
            nat_result = client.get_nat_by_private_ip(network_domain_id, ansible_gw_private_ipv4)
            if nat_result:
                public_ipv4 = nat_result.get('externalIp')
            else:
                public_ipv4 = client.get_next_public_ipv4(network_domain_id).get('ipAddress')
                create_nat_rule(module, client, network_domain_id, ansible_gw_private_ipv4, public_ipv4)
                changed = True
            # Check if the Firewall rule exists and if not create it
            fw_result = client.get_fw_rule_by_name(network_domain_id, ACL_RULE_NAME)
            if fw_result:
                update_fw_rule(module, client, fw_result, network_domain_id, public_ipv4)
            else:
                create_fw_rule(module, client, network_domain_id, public_ipv4)
                changed = True
            return_data['server_id'] = ansible_gw.get('id')
            return_data['password'] = ansible_gw.get('password')
            return_data['internal_ipv4'] = ansible_gw_private_ipv4
            return_data['ipv6'] = ansible_gw.get('networkInfo').get('primaryNic').get('ipv6')
            return_data['public_ipv4'] = public_ipv4
            sleep(10)
            module.exit_json(changed=changed, data=return_data)
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
            module.fail_json(changed=changed, msg='Failed to create/update the Ansible gateway - {0}'.format(exc), exception=traceback.format_exc())
    elif state == 'absent':
        nat_result = public_ipv4 = None
        try:
            # Check if the server exists and remove it
            if ansible_gw:
                delete_server(module, client, ansible_gw)
            # Check if the Firewall rule exists and if not create it
            fw_result = client.get_fw_rule_by_name(network_domain_id, ACL_RULE_NAME)
            if fw_result:
                delete_fw_rule(module, client, network_domain_id, fw_result.get('name'))
            '''
            Cases may exist where the only either the NAT private or public address maybe know so
            two ensure we've checked all possible options we will search by both
            The private address can be found from the server/ansible_gw object but the public address
            can only be determined by the firewall rule desintation value
            '''
            if ansible_gw:
                ansible_gw_private_ipv4 = ansible_gw.get('networkInfo').get('primaryNic').get('privateIpv4')
                nat_result = client.get_nat_by_private_ip(network_domain_id, ansible_gw_private_ipv4)
                if nat_result:
                    public_ipv4 = nat_result.get('externalIp')
            elif fw_result:
                public_ipv4 = fw_result.get('destination').get('ip').get('address')
                nat_result = client.get_nat_by_public_ip(network_domain_id, public_ipv4)

            if nat_result:
                delete_nat_rule(module, client, nat_result.get('id'))
            if public_ipv4:
                public_ip_block = client.get_public_ipv4_by_ip(network_domain_id, public_ipv4)
                if public_ip_block:
                    if not client.check_public_block_in_use(network_domain_id, public_ip_block.get('baseIp')):
                        delete_public_ipv4(module, client, public_ip_block.get('id'))
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
            module.fail_json(changed=changed, msg='Failed to remove the Ansible gateway configuration - {0}'.format(e))

        module.exit_json(changed=True, msg='The Ansible gateway and associated NAT and firewall rules have been removed')
    else:
        module.exit_json(changed=False, msg='Nothing to remove')


if __name__ == '__main__':
    main()
