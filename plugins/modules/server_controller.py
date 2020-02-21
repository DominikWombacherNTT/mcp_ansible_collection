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
module: server_controller
short_description: Add or remove a disk controller configuration for an existing server
description:
    - Add or remove a disk controller configuration for an existing server
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
    network_domain:
        description:
            - The name of the Cloud Network Domain
        required: true
        type: str
    server:
        description:
            - The name of the server
        required: true
        type: str
    type:
        description:
            - The type of controller for this disk
            - Currently this is limited to SCSI controllers only
        required: false
        type: str
        default: SCSI
        choices:
            - SCSI
    controller_number:
        description:
            - The bus number on the controller as an integer
        required: false
        type: int
    adapter_type:
        description:
            - The type of controller adapter to be added
        required: false
        type: str
        default: LSI_LOGIC_PARALLEL
        choices:
            - LSI_LOGIC_PARALLEL
            - LSI_LOGIC_SAS
            - VMWARE_PARAVIRTUAL
            - BUS_LOGIC
    stop:
        description:
            - Should the server be stopped if it is running
            - Disk operations can only be performed while the server is stopped
        required: false
        type: bool
        default: True
    start:
        description:
            - Should the server be started after the disk operations have completed
        required: false
        type: bool
        default: true
    wait:
        description:
            - Should Ansible wait for the task to complete before continuing
        required: false
        type: bool
        default: true
    wait_time:
        description: The maximum time the Ansible should wait for the task to complete in seconds
        required: false
        type: int
        default: 1200
    wait_poll_interval:
        description:
            - The time in between checking the status of the task in seconds
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

  - name: Add a controller to a server
    server_controller:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      adapter_type: VMWARE_PARAVIRTUAL
      state: present

  - name: Delete a controller from a server
    server_controller:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      controller_number: 1
      state: absent
'''

RETURN = '''
data:
    description: Server objects
    returned: success
    type: complex
    contains:
        started:
            description: Is the server running
            type: bool
            returned: when state == present and wait is True
        guest:
            description: Information about the guest OS
            type: complex
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
            sample: "2019-01-14T11:12:31.000Z"
        datacenterId:
            description: Datacenter id/location
            type: str
            returned: when state == present and wait is True
            sample: NA9
        scsiController:
            description: List of the SCSI controllers and disk configuration for the image
            type: complex
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
            sample: NORMAL
        tag:
            description: List of informational tags associated with the server
            type: complex
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
            sample: 4
        id:
            description: The UUID of the server
            type: str
            returned: when state == present
            sample:  b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
        sataController:
            description: List of SATA controllers on the server
            type: list
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
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
            returned: when state == present and wait is True
        name:
            description: The name of the server
            type: str
            returned: when state == present and wait is True
            sample: my_server
'''

import traceback
from time import sleep
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions
from ansible_collections.nttmcp.mcp.plugins.module_utils.config import SCSI_ADAPTER_TYPES
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException

CORE = {
    'module': None,
    'client': None,
    'region': None,
    'datacenter': None,
    'network_domain_id': None,
    'name': None,
    'wait_for_vmtools': False}


def add_controller(module, client, network_domain_id, server):
    """
    Add a controller to an existing server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :returns: The updated server
    """
    name = server.get('name')
    datacenter = server.get('datacenterId')
    controller_type = module.params.get('type')
    adapter_type = module.params.get('adapter_type')
    wait = module.params.get('wait')
    wait_poll_interval = module.params.get('wait_poll_interval')

    if controller_type == 'SCSI':
        controller_name = 'scsiController'
    elif controller_type == 'SATA':
        controller_name = 'sataController'
    elif controller_type == 'IDE':
        controller_name = 'ideController'
    else:
        module.fail_json(msg='Invalid disk type.')

    try:
        controller_number = len(server.get(controller_name))
        client.add_controller(server.get('id'), controller_name, adapter_type, controller_number)
        if wait:
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False, wait_poll_interval)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not create the controller - {0}'.format(e))


def get_controller(module, server):
    """
    Get a controller to an existing server

    :arg module: The Ansible module instance
    :arg server: The dict containing the server
    :returns: The controller(s)
    """
    controller_type = module.params.get('type')
    controller_number = module.params.get('controller_number')
    if controller_number is None:
        return None
    if controller_type == 'SCSI':
        controller_name = 'scsiController'
    elif controller_type == 'SATA':
        controller_name = 'sataController'
    elif controller_type == 'IDE':
        controller_name = 'ideController'
    else:
        module.fail_json(msg='Invalid disk type.')

    try:
        return server.get(controller_name)[controller_number]
    except (IndexError, AttributeError):
        return None
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not locate any matching controller - {0}'.format(e))
    return None


def remove_controller(module, client, network_domain_id, server, controller):
    """
    Delete a controller to an existing server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :arg controller: The dict containing the controller to remove
    :returns: The updated server
    """
    name = server.get('name')
    datacenter = server.get('datacenterId')
    wait_poll_interval = module.params.get('wait_poll_interval')
    try:
        client.remove_controller(controller.get('id'))
        if module.params.get('wait'):
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False, wait_poll_interval)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not remove the controller {0} - {1}'.format(controller.get('id'), e))


def server_command(module, client, server, command):
    """
    Send a command to a server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :returns: The updated server
    """
    name = server.get('name')
    datacenter = server.get('datacenterId')
    network_domain_id = server.get('networkInfo').get('networkDomainId')
    wait = module.params.get('wait')
    check_for_start = True
    check_for_stop = False
    # Set a default timer unless a lower one has been provided
    if module.params.get('wait_poll_interval') < 15:
        wait_poll_interval = module.params.get('wait_poll_interval')
    else:
        wait_poll_interval = 15

    try:
        if command == "start":
            client.start_server(server_id=server.get('id'))
        elif command == "reboot":
            client.reboot_server(server_id=server.get('id'))
        elif command == "stop":
            client.shutdown_server(server_id=server.get('id'))
            check_for_start = False
            check_for_stop = True
        if wait:
            if command == 'start' or command == 'reboot':
                # Temporarily enable waiting for VMWare Tools
                CORE['wait_for_vmtools'] = True
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', check_for_start, check_for_stop, wait_poll_interval)
            if command == 'start' or command == 'reboot':
                # Disable any waiting for VMWare Tools
                CORE['wait_for_vmtools'] = False
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not {0} the server - {1}'.format(command, e))


def wait_for_server(module, client, name, datacenter, network_domain_id, state, check_for_start=False, check_for_stop=False, wait_poll_interval=None):
    """
    Wait for an operation on a server. Polls based on wait_time and wait_poll_interval values.

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg name: The name of the server
    :arg datacenter: The name of a MCP datacenter
    :arg network_domain_id: The UUID of the Cloud Network Domain
    :arg state: The desired state to wait
    :arg check_for_start: Check if the server is started
    :arg check_for_stop: Check if the server is stopped
    :arg wait_poll_interval: The time between polls
    :returns: The server dict
    """
    set_state = False
    actual_state = ''
    start_state = ''
    time = 0
    vmtools_status = False
    wait_for_vmtools = CORE.get('wait_for_vmtools')
    wait_time = module.params.get('wait_time')
    if wait_poll_interval is None:
        wait_poll_interval = module.params.get('wait_poll_interval')
    server = []
    while not set_state and time < wait_time:
        try:
            servers = client.list_servers(datacenter=datacenter, network_domain_id=network_domain_id)
        except NTTMCPAPIException as e:
            module.fail_json(msg='Failed to get a list of servers - {0}'.format(e), exception=traceback.format_exc())
        server = [x for x in servers if x['name'] == name]
        # Check if VMTools has started - if the user as specified to wait for VMWare Tools to be running
        try:
            if wait_for_vmtools:
                if server[0].get('guest').get('vmTools').get('runningStatus') == 'RUNNING':
                    vmtools_status = True
        except AttributeError:
            pass
        except IndexError:
            module.fail_json(msg='Failed to find the server - {0}'.format(name))
        try:
            actual_state = server[0]['state']
            start_state = server[0]['started']
        except (KeyError, IndexError) as e:
            module.fail_json(msg='Failed to find the server - {0}'.format(name))
        if actual_state != state:
            wait_required = True
        elif check_for_start and not start_state:
            wait_required = True
        elif check_for_stop and start_state:
            wait_required = True
        elif wait_for_vmtools and not vmtools_status:
            wait_required = True
        else:
            wait_required = False

        if wait_required:
            sleep(wait_poll_interval)
            time = time + wait_poll_interval
        else:
            set_state = True

    if server and time >= wait_time:
        module.fail_json(msg='Timeout waiting for the server to be created')

    return server[0]


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
            network_domain=dict(required=True, type='str'),
            server=dict(required=True, type='str'),
            type=dict(default='SCSI', required=False, choices=['SCSI']),
            controller_number=dict(required=False, type='int'),
            adapter_type=dict(default='LSI_LOGIC_PARALLEL', choices=SCSI_ADAPTER_TYPES),
            state=dict(default='present', choices=['present', 'absent']),
            stop=dict(default=True, type='bool'),
            start=dict(default=True, type='bool'),
            wait=dict(required=False, default=True, type='bool'),
            wait_time=dict(required=False, default=1200, type='int'),
            wait_poll_interval=dict(required=False, default=30, type='int')
        ),
        supports_check_mode=True
    )

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    name = module.params.get('server')
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
    network_domain_name = module.params.get('network_domain')
    CORE['datacenter'] = module.params.get('datacenter')
    CORE['region'] = module.params.get('region')
    server_running = True
    stop_server = module.params.get('stop')
    start = module.params.get('start')
    server = {}

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Could not load the user credentials')

    client = NTTMCPClient(credentials, module.params.get('region'))

    # Get the CND object based on the supplied name
    try:
        if network_domain_name is None:
            module.fail_json(msg='No network_domain or network_info.network_domain was provided')
        network = client.get_network_domain_by_name(datacenter=datacenter, name=network_domain_name)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException):
        module.fail_json(msg='Failed to find the Cloud Network Domain: {0}'.format(network_domain_name))

    # Check if the Server exists based on the supplied name
    try:
        server = client.get_server_by_name(datacenter, network_domain_id, None, name)
        if server:
            server_running = server.get('started')
        else:
            module.fail_json(msg='Failed to find the server - {0}'.format(name))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed attempting to locate any existing server - {0}'.format(e))

    # Setup the rest of the CORE dictionary to save passing data around
    CORE['network_domain_id'] = network_domain_id
    CORE['module'] = module
    CORE['client'] = client
    CORE['name'] = server.get('name')

    if state == 'present':
        controller = get_controller(module, server)
        if not controller:
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='A new {0} controller of type {1} will be added to the server {2}'.format(
                    module.params.get('type'),
                    module.params.get('adapter_type'),
                    server.get('name')))
            if server_running and stop_server:
                server_command(module, client, server, 'stop')
                server_running = False
            elif server_running and not stop_server:
                module.fail_json(msg='Controllers cannot be added while the server is running')
            add_controller(module, client, network_domain_id, server)
            if start and not server_running:
                server_command(module, client, server, 'start')
            server = client.get_server_by_name(datacenter, network_domain_id, None, name)
            module.exit_json(changed=True, data=server)
        else:
            module.exit_json(changed=False, data=server)
    elif state == 'absent':
        try:
            controller = get_controller(module, server)
            if not controller:
                module.fail_json(msg='Server {0} has no {1} controller {2}'.format(
                    server.get('name'),
                    module.params.get('type'),
                    module.params.get('controller_number')))
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='The {0} controller of type {1} with ID {2} will be removed to the server {3}'.format(
                    module.params.get('type'),
                    controller.get('adapter_type'),
                    controller.get('id'),
                    server.get('name')))
            if server_running and stop_server:
                server_command(module, client, server, 'stop')
                server_running = False
            elif server_running and not stop_server:
                module.fail_json(msg='Controllers cannot be removed while the server is running')
            remove_controller(module, client, network_domain_id, server, controller)
            # Introduce a pause to allow the API to catch up in more remote MCP locations
            sleep(10)
            if start and not server_running:
                server_command(module, client, server, 'start')
            server = client.get_server_by_name(datacenter, network_domain_id, None, name)
            module.exit_json(changed=True, data=server)
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
            module.fail_json(msg='Could not delete the controller - {0}'.format(e))


if __name__ == '__main__':
    main()
