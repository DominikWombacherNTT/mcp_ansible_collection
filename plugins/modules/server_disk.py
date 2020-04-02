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
module: server_disk
short_description: Alter the disk configuration for an existing server
description:
    - Alter the disk configuration for an existing server
    - The controller must exist before trying to add a disk of that type. E.g. If no IDE controller exists on a server,
    - trying to add a disk here using a controller type of IDE will fail
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
        required: true
        type: str
    server:
        description:
            - The name of the server
        required: true
        type: str
    id:
        description:
            - The UUID of the disk
        required: false
        type: str
    type:
        description:
            - The type of controller for this disk
        required: false
        type: str
        default: SCSI
        choices:
            - SCSI
            - SATA
            - IDE
    controller_number:
        description:
            - The controller number on the bus as an integer
        required: false
        type: int
        default: 0
    disk_number:
        description:
            - The disk number on the controller as an integer
            - If no disk number is provided the next free disk on the specified type on the controller will be assumed
        required: false
        type: int
        default: 0
    size:
        description:
            - The new size of the disk as an integer
        required: false
        type: int
    speed:
        description:
            - The new speed of the disk
        required: false
        type: str
        default: STANDARD
        choices:
            - STANDARD
            - ECONOMY
            - HIGHPERFORMANCE
            - PROVISIONEDIOPS
    iops:
        description:
            - The IOPS for the disk as an integer
            - Only used for PROVISIONEDIOPS
            - If no value is provided and the current IOPS is less than 3 x
            - the new disk size a new IOPS count of 3 x the new disk size will be applied.
        required: false
        type: int
    stop:
        description:
            - Should the server be stopped if it is running
            - Disk operations can only be performed while the server is stopped
        required: false
        type: bool
        default: true
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
    wait_for_vmtools:
        description:
            - Should Ansible wait for VMWare Tools to be running before continuing
            - This should only be used for server images that are running VMWare Tools
            - This should not be used for NGOC (Non Guest OS Customization) servers/images
        required: false
        type: bool
        default: false
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

  - name: Add a disk to a server
    server_disk:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      size: 10
      speed: STANDARD
      state: present

  - name: Add a Provisioned IOPs disk to a server
    server_disk:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      size: 10
      speed: PROVISIONEDIOPS
      iops: 30
      state: present
      start: False

  - name: Update a disk on a server (PIOPS)
    server_disk:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      controller_number: 0
      disk_number: 1
      speed: PROVISIONEDIOPS
      size: 100
      iops: 1000
      state: present

  - name: Update a disk on a server by controller and disk number
    server_disk:
      region: na
      datacenter: NA12
      network_domain: myCND
      server: myServer01
      type: SCSI
      controller_number: 0
      disk_number: 0
      speed: STANDARD
      state: present

  - name: Delete a disk
    server_disk:
      region: na
      datacenter: NA12
      network_domain: myCND
      name: myServer01
      controller_number: 0
      disk_number: 1
      state: absent
'''

RETURN = '''
disk_number:
    description: The number of the new disk on the controller
    returned: success when adding a new disk
    type: int
    sample: 1
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
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, compare_json
from ansible_collections.nttmcp.mcp.plugins.module_utils.config import (DISK_SPEEDS, IOPS_MULTIPLIER, DISK_CONTROLLER_TYPES,
                                                                        MAX_IOPS_PER_GB, MAX_DISK_SIZE, MAX_DISK_IOPS)
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException

CORE = {
    'module': None,
    'client': None,
    'region': None,
    'datacenter': None,
    'network_domain_id': None,
    'name': None,
    'wait_for_vmtools': False}


def add_disk(module, client, network_domain_id, server):
    """
    Add a disk to an existing server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :returns: The updated server
    """
    device_number = None
    name = server.get('name')
    datacenter = server.get('datacenterId')
    disk_speed = module.params.get('speed')
    disk_type = module.params.get('type')
    disk_iops = module.params.get('iops')
    disk_size = module.params.get('size')
    controller_number = module.params.get('controller_number')
    if controller_number is None:
        module.fail_json(msg='The controller number cannot be None')
    module.params.get('wait')
    wait_poll_interval = module.params.get('wait_poll_interval')

    # Check IOPS count is within minimum spec
    if disk_type == 'PROVISIONEDIOPS':
        disk = {
            'sizeGb': disk_size,
            'speed': disk_speed,
            'iops': disk_iops
        }
        disk_iops = validate_disk_iops(disk, disk_size, disk_iops)

    if disk_type == 'SCSI':
        controller_name = 'scsiController'
    elif disk_type == 'SATA':
        controller_name = 'sataController'
    elif disk_type == 'IDE':
        controller_name = 'ideController'
    else:
        module.fail_json(msg='Invalid disk type.')

    try:
        device_number = get_next_free_disk(disk_type, server.get(controller_name)[controller_number])
        if device_number is None:
            module.fail_json(msg='Error: Could not locate a valid free disk ID on this controller')
        controller_id = server.get(controller_name)[controller_number].get('id')
        client.add_disk(controller_id, controller_name, device_number, disk_size, disk_speed, disk_iops)
        if module.params.get('wait'):
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False, wait_poll_interval)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not create the disk - {0}'.format(e))

    return device_number


def get_next_free_disk(disk_type, controller):
    valid_slots = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15]
    used_slots = list()
    if disk_type == 'SCSI':
        used_slots = [item['scsiId'] for item in controller.get('disk', list())]
    elif disk_type == 'SATA':
        used_slots = [item['sataId'] for item in controller.get('disk', list())]
    elif disk_type == 'IDE':
        used_slots = [item['ideId'] for item in controller.get('disk', list())]

    for slot in valid_slots:
        if slot not in used_slots:
            return slot
    return None


def update_disk(module, client, network_domain_id, server, disk):
    """
    Update a disk on an existing server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :arg disk: The dict containing the disk to be udpated
    :returns: The updated server
    """
    name = server.get('name')
    datacenter = server.get('datacenterId')
    disk_speed = module.params.get('speed')
    disk_id = disk.get('id')
    disk_iops = module.params.get('iops')
    disk_size = module.params.get('size')
    module.params.get('wait')
    wait_poll_interval = module.params.get('wait_poll_interval')

    # Make any changes required to the disk speed first
    try:
        if disk_speed and (disk_speed != disk.get('speed')):
            if disk_speed == 'PROVISIONEDIOPS':
                # Set the initial IOPS to the minimum for the current size of the disk - any changes will be made later
                client.update_disk_speed(disk_id, disk_speed, disk.get('sizeGb') * IOPS_MULTIPLIER)
            else:
                client.update_disk_speed(disk_id, disk_speed, None)
            if module.params.get('wait'):
                wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False, wait_poll_interval)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not update the disk speed for disk ID {0} - {1}'.format(disk.get('id'), e))

    # Handle size changes to non PROVISIONEDIOPS disks
    if disk_speed != 'PROVISIONEDIOPS':
        try:
            if disk_size and disk_size != disk.get('sizeGb'):
                expand_disk(module, client, server, disk)
                if module.params.get('wait'):
                    wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False, wait_poll_interval)
        except (KeyError, IndexError, NTTMCPAPIException) as e:
            module.fail_json(msg='Could not update the disk {0} - {1}'.format(disk.get('id'), e))
    else:
        # Handle size and IOPS increases for PROVISIONEDIOPS disks
        # Check IOPS count is within minimum spec
        disk_iops = validate_disk_iops(disk, disk_size, disk_iops)
        if (disk_iops != disk.get('iops')) or (disk_size != disk.get('sizeGb')):
            try:
                expand_piops_disk(server.get('id'), disk, disk_size, disk_iops)
            except NTTMCPAPIException as e:
                module.fail_json(msg='Could not update the disk size and or IOPS as required: {0}'.format(e))


def expand_piops_disk(server_id, disk, new_disk_size, new_disk_iops):
    """
    Wrapper function for expanding the size and iops on a provisioned IOPS disk

    :arg server_id: The UUID of the server
    :arg disk: The disk dictionary
    :arg new_disk_size: The end state size in GB
    :arg new_disk_iops: The final state IOPS count
    :returns: Nothing
    """
    if new_disk_size > MAX_DISK_SIZE:
        CORE.get('module').fail_json(msg='The disk size {0} is greater than the maximum allowed disk size {1}'.format(new_disk_size, MAX_DISK_SIZE))
    if new_disk_iops > MAX_DISK_IOPS:
        CORE.get('module').fail_json(msg='The disk iops {0} is greater than the maximum allowed disk IOPS {1}'.format(new_disk_iops, MAX_DISK_IOPS))
    try:
        update_piops_disk(server_id, disk.get('id'), disk.get('sizeGb'), disk.get('iops'), new_disk_size, new_disk_iops)
    except NTTMCPAPIException as e:
        CORE.get('module').fail_json(msg='Error modifying the disk {0}: {1}'.format(disk.get('id'), e))


def update_piops_disk(server_id, disk_id, current_size, current_iops, final_size, final_iops):
    """
    Handle the task increasing both IOPS and size on a provisioned IOPS disk in the correct order

    :arg server_id: The UUID of the server
    :arg disk_id: The UUID of the disk
    :arg current_iops: The current IOPS value for the disk
    :arg final_size: The end state size in GB
    :arg final_iops: The final state IOPS count
    :returns: Nothing
    """
    while current_size != final_size or current_iops != final_iops:
        current_max_iops = current_size * MAX_IOPS_PER_GB
        # Handle cases where the user did not specify an IOP count in the playbook
        if not final_iops:
            final_iops = IOPS_MULTIPLIER * final_size
        new_size = int(current_max_iops / IOPS_MULTIPLIER)
        if final_iops != current_iops and current_max_iops != current_iops:
            if current_max_iops < final_iops:
                CORE.get('client').change_iops(disk_id, current_max_iops)
                current_iops = current_max_iops
            else:
                if not current_iops > final_iops:
                    CORE.get('client').change_iops(disk_id, final_iops)
                    current_iops = final_iops

            wait_result = wait_for_server(CORE.get('module'), CORE.get('client'), CORE.get('name'), CORE.get('datacenter'),
                                          CORE.get('network_domain_id'), 'NORMAL', False, False, 10)
            if not wait_result:
                CORE.get('module').fail_json(msg='Timeout. Could not verify the server update was successful. Check manually')

        if final_size != current_size:
            if new_size < final_size:
                CORE.get('client').expand_disk(server_id=server_id, disk_id=disk_id, disk_size=new_size)
                current_size = new_size
            else:
                if not current_size > final_size:
                    CORE.get('client').expand_disk(server_id=server_id, disk_id=disk_id, disk_size=final_size)
                    current_size = final_size

            wait_result = wait_for_server(CORE.get('module'), CORE.get('client'), CORE.get('name'), CORE.get('datacenter'),
                                          CORE.get('network_domain_id'), 'NORMAL', False, False, 10)
            if not wait_result:
                CORE.get('module').fail_json(msg='Timeout. Could not verify the server update was successful. Check manually')


def get_disk_by_id(server, disk_id):
    '''
    Get a disk object by the UUID

    :arg module: The Ansible module instance
    :arg server: The existing server object
    :arg disk_id: The UUID of the disk
    :returns: The located disk object or None
    '''
    for controller in DISK_CONTROLLER_TYPES:
        try:
            for controller_instance in server.get(controller):
                for disk in controller_instance.get('disk'):
                    if disk_id == disk.get('id'):
                        return disk
        except (IndexError, KeyError, AttributeError):
            pass
    return None


def compare_disk(module, existing_disk):
    """
    Compare two disks

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg existing_disk: The dict of the existing disk to be compared to
    :returns: Any differences between the two disk
    """
    new_disk = deepcopy(existing_disk)

    disk_size = module.params.get('size')
    disk_speed = module.params.get('speed')
    disk_iops = module.params.get('iops')

    if disk_size:
        new_disk['sizeGb'] = disk_size
    if disk_speed:
        new_disk['speed'] = disk_speed
    if disk_iops:
        new_disk['iops'] = disk_iops

    compare_result = compare_json(new_disk, existing_disk, None)
    # Implement Check Mode
    if module.check_mode:
        module.exit_json(data=compare_result)
    return compare_result.get('changes')


def validate_disk_iops(disk, disk_size, disk_iops):
    '''
    Validate the IOPS count is correct for the specified disk and disk size

    :arg disk: The disk object
    :arg disk_size: The new disk size in GB
    :arg disk_iops: The new disk IOPS as specified in the argument spec
    :returns: The specified IOPS count if valid or the minimum valid count
    '''
    if disk.get('speed') == 'PROVISIONEDIOPS':
        existing_disk_iops = disk.get('iops')
        if disk_iops:
            if not disk_iops > (disk_size * IOPS_MULTIPLIER):
                disk_iops = disk_size * IOPS_MULTIPLIER
        else:
            if not existing_disk_iops > (disk_size * IOPS_MULTIPLIER):
                disk_iops = disk_size * IOPS_MULTIPLIER
    else:
        if not disk_iops > (disk_size * IOPS_MULTIPLIER):
            disk_iops = disk_size * IOPS_MULTIPLIER
    return disk_iops


def get_disk(module, server):
    """
    Get a disk from an existing server

    :arg module: The Ansible module instance
    :arg server: The dict containing the server
    :returns: The disk(s)
    """
    disk_type = module.params.get('type')
    disk_number = module.params.get('disk_number')
    controller_number = module.params.get('controller_number')
    if controller_number is None:
        module.fail_json(msg='The controller number cannot be None')
    if disk_type == 'SCSI':
        controller_name = 'scsiController'
    elif disk_type == 'SATA':
        controller_name = 'sataController'
    elif disk_type == 'IDE':
        controller_name = 'ideController'
    else:
        module.fail_json(msg='Invalid disk type.')

    try:
        if disk_number is not None:
            return server.get(controller_name)[controller_number].get('disk')[disk_number]
        else:
            return None
    except (NTTMCPAPIException) as e:
        module.fail_json(msg='Could not locate any matching disk - {0}'.format(e))
    except (KeyError, IndexError, AttributeError):
        return None


def expand_disk(module, client, server, disk):
    """
    Expand a existing disk

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg server: The dict containing the server to be updated
    :arg disk: The dict containing the disk to be deleted
    :returns: The updated server
    """
    disk_id = disk.get('id')
    disk_size = module.params.get('size')
    if disk_id is None:
        module.fail_json(changed=False, msg='No disk id provided.')
    if disk_size is None:
        module.fail_json(msg='No size was provided. A value larger than 10 is required for disk_size.')
    server_id = server.get('id')
    try:
        client.expand_disk(server_id=server_id, disk_id=disk_id, disk_size=disk_size)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not expand the disk - {0}'.format(e))
    return True


def remove_disk(module, client, network_domain_id, server, disk):
    """
    Delete a disk to an existing server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :arg server: The dict containing the server to be updated
    :arg disk: The dict containing the disk to be deleted
    :returns: The updated server
    """
    name = server.get('name')
    datacenter = server.get('datacenterId')
    wait_poll_interval = module.params.get('wait_poll_interval')
    try:
        client.remove_disk(disk.get('id'))
        if module.params.get('wait'):
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', False, False,
                            wait_poll_interval)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not remove the disk {0} - {1}'.format(disk.get('id'), e))


def server_command(module, client, server, command):
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
            if module.params.get('wait_for_vmtools') and (command == 'start' or command == 'reboot'):
                # Temporarily enable waiting for VMWare Tools
                CORE['wait_for_vmtools'] = True
            wait_for_server(module, client, name, datacenter, network_domain_id, 'NORMAL', check_for_start,
                            check_for_stop, wait_poll_interval)
            if module.params.get('wait_for_vmtools') and (command == 'start' or command == 'reboot'):
                # Disable any waiting for VMWare Tools
                CORE['wait_for_vmtools'] = False
    except NTTMCPAPIException as e:
        module.fail_json(msg='Could not {0} the server - {1}'.format(command, e))


def wait_for_server(module, client, name, datacenter, network_domain_id, state, check_for_start=False,
                    check_for_stop=False, wait_poll_interval=None):
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
    wait_required = False
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
            if len(server) > 0:
                actual_state = server[0]['state']
                start_state = server[0]['started']
        except (KeyError, IndexError):
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
            id=dict(default=None, required=False, type='str'),
            type=dict(default='SCSI', required=False, choices=['SCSI', 'SATA', 'IDE']),
            controller_number=dict(default=0, required=False, type='int'),
            disk_number=dict(default=None, required=False, type='int'),
            size=dict(required=False, type='int'),
            speed=dict(default='STANDARD', required=False, choices=DISK_SPEEDS),
            iops=dict(default=None, required=False, type='int'),
            state=dict(default='present', choices=['present', 'absent']),
            stop=dict(default=True, type='bool'),
            start=dict(default=True, type='bool'),
            wait=dict(required=False, default=True, type='bool'),
            wait_time=dict(required=False, default=1200, type='int'),
            wait_poll_interval=dict(required=False, default=30, type='int'),
            wait_for_vmtools=dict(required=False, default=False, type='bool')
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
    # CORE['wait_for_vmtools'] = module.params.get('wait_for_vmtools')
    server_running = True
    stop_server = module.params.get('stop')
    start = module.params.get('start')
    server = {}
    disk_number = None

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
        disk = get_disk(module, server)
        if not disk:
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='A new {0} disk of size {1} will be added to the server {2}'.format(
                    module.params.get('type'),
                    module.params.get('size'),
                    server.get('name')))
            if server_running and stop_server:
                server_command(module, client, server, 'stop')
                server_running = False
            elif server_running and not stop_server:
                module.fail_json(msg='Server disks cannot be added while the server is running')
            disk_number = add_disk(module, client, network_domain_id, server)
            if start and not server_running:
                server_command(module, client, server, 'start')
            server = client.get_server_by_name(datacenter, network_domain_id, None, name)
            module.exit_json(changed=True, disk_number=disk_number, data=server)
        else:
            try:
                if compare_disk(module, disk):
                    if server_running and stop_server:
                        server_command(module, client, server, 'stop')
                        server_running = False
                    elif server_running and not stop_server:
                        module.fail_json(msg='Server disks cannot be added while the server is running')
                    update_disk(module, client, network_domain_id, server, disk)
                else:
                    module.exit_json(changed=False, data=server)
                if start and not server_running:
                    server_command(module, client, server, 'start')
                server = client.get_server_by_name(datacenter, network_domain_id, None, name)
                module.exit_json(changed=True, data=server)
            except NTTMCPAPIException as e:
                module.fail_json(msg='Failed to update the disk - {0}'.format(e))
    elif state == 'absent':
        try:
            disk = get_disk(module, server)
            if not disk:
                module.fail_json(msg='Controller {0} has no disk {1}'.format(module.params.get('controller_number'),
                                 module.params.get('disk_number')))
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='The disk with ID {0} will be removed from the server {1}'.format(
                    disk.get('id'),
                    server.get('name')))
            if server_running and stop_server:
                server_command(module, client, server, 'stop')
                server_running = False
            elif server_running and not stop_server:
                module.fail_json(msg='Disks cannot be removed while the server is running')
            remove_disk(module, client, network_domain_id, server, disk)
            # Introduce a pause to allow the API to catch up in more remote MCP locations
            sleep(10)
            server = client.get_server_by_name(datacenter, network_domain_id, None, name)
            if server:
                server_running = server.get('started')
            else:
                module.fail_json(msg='Failed to find the server to determine the final running state - {0}'.format(name))
            if start and not server_running:
                server_command(module, client, server, 'start')
            server = client.get_server_by_name(datacenter, network_domain_id, None, name)
            module.exit_json(changed=True, data=server)
        except (KeyError, IndexError, NTTMCPAPIException) as e:
            module.fail_json(msg='Could not delete the disk - {0}'.format(e))


if __name__ == '__main__':
    main()
