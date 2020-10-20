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
module: snapshot_info
short_description: List/Get information about Snapshots
description:
    - List/Get information about Snapshots
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
        type: str
        default: na
    datacenter:
        description:
            - The datacenter name
        required: false
        type: str
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: false
        type: str
    server:
        description:
            - The name of a server to enable Snapshots on
        required: false
        type: str
    server_id:
        description:
            - The UUID of a server to enable Snapshots on
        required: false
        type: str
    plan:
        description:
            - The name of a desired Service Plan. Use snapshot_info to get a list of valid plans.
        required: false
        type: str
    type:
        description:
            - The type of entity to get/list information about
        required: false
        default: window
        type: str
        choices:
            - window
            - plan
            - snapshot
            - server
    window:
        description:
            - The starting hour for the snapshot window/window (24 hour notation).
            - Use snapshot_info to find a window.
        required: false
        type: int
    slots_available:
        description:
            - Only show windows with slots available
        required: false
        default: True
        type: bool
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

  - name: List Snapshot Windows
    snapshot_info:
      region: na
      datacenter: NA9
      plan: ONE_MONTH

  - name: Get a specific Snapshot Window for 8am
    snapshot_info:
      region: na
      datacenter: NA9
      plan: ONE_MONTH
      window: 8

  - name: List Snapshot Plans
    snapshot_info:
      region: na
      datacenter: NA9
      type: plan

  - name: Get the Snapshot service configuration for a server
    snapshot_info:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      type: server

  - name: Get a list of Snapshots for a configured server
    snapshot_info:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      type: snapshot

'''
RETURN = '''
data:
    description: Snapshot objects
    returned: success
    type: complex
    contains:
        count:
            description: The number of entities returned
            returned: on a list operation
            type: int
            sample: 1
        snapshot_plan_info:
            description: List of Snapshot Plans
            returned: type == plan
            type: complex
            contains:
                available:
                    description: When "true" indicates that the plan is available for use
                    returned: success
                    type: bool
                description:
                    description: More detailed description of what comprises the plan.
                    returned: success
                    type: str
                    sample: "Daily Snapshots retained for 14 Days, Weekly Snapshots retained for 90 Days"
                displayName:
                    description: Simple text display name. Useful for reference and display in UI integration.
                    type: str
                    sample: "One Month: 7d-4w"
                id:
                    description: String UID or UUID identifying the entity
                    returned: success
                    type: str
                    sample: ONE_MONTH or d62596e8-fe2b-44ba-8ad2-a669b9dfcb51
                snapshotFrequency:
                    description: The frequency of SYSTEM snapshots for the plan. Values are DAILY and WEEKLY
                    returned: success
                    type: str
                    sample: DAILY
                supportsReplication:
                    description: When True indicates that the plan supports Snapshot Replication
                    returned: success
                    type: str
        server_snaphot_info:
            description: The Snapshot configuration for a server
            returned: type == server
            type: complex
            contains:
                manualSnapshotInProgress:
                    description: Is a manual Snapshot currently being processed
                    returned: success
                    type: bool
                servicePlan:
                    description: The type fo Snapshot Plan configured for this server
                    returned: success
                    type: str
                    sample: ONE_MONTH
                state:
                    description: Simple text display name. Useful for reference and display in UI integration.
                    type: str
                    sample: "One Month: 7d-4w"
                window:
                    description: The window for the configured Snapshot service
                    returned: success
                    type: complex
                    contains:
                        dayOfWeek:
                            description: Which day it the Snapshot is taken on (this should always be daily)
                            returned: success
                            type: str
                            sample: DAILY
                        startHour:
                            description: Snapshot Windows begin on 2 hour periods
                            returned: success
                            type: str
                            sample: 8
        snapshot_window_info:
            description: List of Snapshot Windows
            returned: type == window
            type: complex
            contains:
                availabilityStatus:
                    description: RESERVED_FOR_MAINTENANCE, AVAILABLE or NOT_CURRENTLY_AVAILABLE
                    returned: success
                    type: str
                    sample: OVERLAPS_WITH_MAINTENANCE
                availableSlotCount:
                    description: The number of available slots in the Snapshot Window
                    returned: success
                    type: int
                    sample: 59
                dayOfWeek:
                    description: Which day it the Snapshot is taken on (this should always be daily)
                    returned: success
                    type: str
                    sample: DAILY
                startHour:
                    description: Snapshot Windows begin on 2 hour periods
                    returned: success
                    type: int
                    sample: 8
                timeZone:
                    description: The timeZone that the Snapshot Window is relative to
                    returned: success
                    type: str
                    sample: Etc/UTC
        snapshot_info:
            description: List of Snapshots for a server
            returned: type == snapshot
            type: complex
            contains:
                indexState:
                    description: Possible values for indexState are INDEX_NOT_COMPLETE, INDEX_VALID, INDEX_INVALID
                    type: str
                    sample: INDEX_VALID
                expiryTime:
                    description: Snapshots exist for a limited period after which the system will remove them
                    type: str
                    sample: "2019-11-22T08:00:05.000Z"
                id:
                    description: UUID identifying the Snapshot.
                    type: str
                    sample: 68138b18-1e08-49bd-96e3-49a4d80e7c62
                datacenterId:
                    description: ID of the datacenter
                    type: str
                    sample: NA12
                state:
                    description: The state of the Snapshot
                    type: str
                    sample: NORMAL
                replica:
                    description:
                        - Boolean identifying whether or not a the Snapshot is local or one replicated
                        - from another Data Center
                    type: bool
                startTime:
                    description: The time at which the system begins the snapshot process.
                    type: str
                    sample: "2019-11-15T08:00:05.000Z"
                serverConfig:
                    description: The specification of the Server at the time the Snapshot was taken
                    type: complex
                    contains:
                        guest:
                            description: Information about the guest OS
                            type: complex
                            contains:
                                osCustomization:
                                    description: Does the image support guest OS customization
                                    type: bool
                                operatingSystem:
                                    description: Operating system information
                                    type: complex
                                    contains:
                                        displayName:
                                            description: The OS display name
                                            type: str
                                            sample: UBUNTU16/64
                                        id:
                                            description: The OS UUID
                                            type: str
                                            sample: UBUNTU1664
                                        family:
                                            description: The OS family
                                            type: str
                                            sample: UNIX
                        networkInfo:
                            description: Server network information
                            type: complex
                            contains:
                                primaryNic:
                                    description: The primary NIC on the server
                                    type: complex
                                    contains:
                                        vlanName:
                                            description: The name of the VLAN the server resides in
                                            type: str
                                            sample: vlan_01
                                        vlanId:
                                            description: The UUID of the VLAN
                                            type: str
                                            sample: b7de0cfd-46d5-4316-845b-d1283245c79f
                                        state:
                                            description: The UUID of the VLAN the server resides in
                                            type: str
                                            sample: NORMAL
                                        privateIpv4:
                                            description: The IPv4 address of the server
                                            type: str
                                            sample: 10.0.0.6
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
                                            sample: 2607:f480:211:1238:3678:58e8:4e42:93fc
                                        networkAdapter:
                                            description: The VMWare NIC type
                                            type: str
                                            sample: VMXNET3
                                        id:
                                            description: The UUID of the NIC
                                            type: str
                                            sample: a616cd9b-82bc-4f8c-bec2-7d58fea88a9c
                                networkDomainId:
                                    description: The UUID of the Cloud Network Domain the server resides in
                                    type: str
                                    sample: 2495e11a-8d52-40f1-9d67-512ade6139ee
                                networkDomainName:
                                    description: The name of the Cloud Network Domain the server resides in
                                    type: str
                                    sample: ansible_test
                        cluster:
                            description: The vCenter cluster for the server
                            type: complex
                            contains:
                                id:
                                    description: The UUID of the cluster
                                    type: str
                                    sample: NA12-01
                                name:
                                    description: The name of the cluster
                                    type: str
                                    sample: Default Cluster
                        memoryGb:
                            description: Server memory in GB
                            type: int
                            sample: 4
                        scsiController:
                            description: List of the SCSI controllers and disk configuration for the image
                            type: list
                            contains:
                                busNumber:
                                    description: The SCSI bus number
                                    type: int
                                    sample: 0
                                state:
                                    description: The state of the SCSI Controller
                                    type: str
                                    sample: NORMAL
                                disk:
                                    description: List of disks associated with this image
                                    type: list
                                    contains:
                                        sizeGb:
                                            description: The initial size of the disk in GB
                                            type: int
                                            sample: 20
                                        state:
                                            description: The state of the disk
                                            type: str
                                            sample: NORMAL
                                        driveType:
                                            description: The type of disk
                                            type: str
                                            sample: DISK
                                        scsiId:
                                            description: The ID of the disk on the controller
                                            type: int
                                            sample: 0
                                        speed:
                                            description: The disk speed
                                            type: str
                                            sample: STANDARD
                                        id:
                                            description: The disk UUID
                                            type: str
                                            sample: 93df19a6-3136-4078-836e-f37aeb139bfd
                                id:
                                    description: The UUID of the SCSI Controller
                                    type: str
                                    sample: 62602df5-10b1-44e4-817a-38b97ca18c48
                                adapterType:
                                    description: the SCSI Controller type
                                    type: str
                                    sample: LSI_LOGIC_PARALLEL
                        virtualHardwareVersion:
                            description: The VM hardware version
                            type: str
                            sample: vmx-10
                        advancedVirtualizationSetting:
                            description: Advanced virtualization settings for the VM
                            type: list
                            contains:
                                name:
                                    description: Advanced VMWare setting
                                    type: str
                                    sample: nestedHardwareVirtualization
                                value:
                                    description: Advanced VMWare setting
                                    type: str
                                    sample: false
                        cpu:
                            description: The CPU specifications for the server
                            type: complex
                            contains:
                                coresPerSocket:
                                    description: The number of cores per socket
                                    type: int
                                    sample: 1
                                count:
                                    description: The number of CPUs
                                    type: int
                                    sample: 2
                                speed:
                                    description: The CPU speed
                                    type: str
                                    sample: STANDARD
                type:
                    description: Indicates whether or not the Snapshot is a SYSTEM scheduled Snapshot or a MANUAL
                    type: str
                    sample: SYSTEM
                createTime:
                    description:
                        - For User initiated Manual Snapshot createTime corresponds to the point in time that
                        - CloudControl processed the Initiate Manual Snapshot for a Server API.
                    type: str
                    sample: "2019-11-15T08:31:22.000Z"
                consistencyLevel:
                    description:
                        - Returned for snapshots which have completed successfully
                        - (have a NORMAL value for state).
                    type: str
                    sample: CRASH_CONSISTENT
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def get_network_domain_id(module, client):
    """
    Get the UUID of a Network Domain

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: The UUID of the Cloud Network Domain
    """
    network_domain_name = module.params.get('network_domain')
    datacenter = module.params.get('datacenter')
    # Get the CND
    try:
        network = client.get_network_domain_by_name(name=network_domain_name, datacenter=datacenter)
        network_domain_id = network.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(e))
    return network_domain_id


def get_server(module, client, network_domain_id):
    """
    Get a server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: The server object
    """
    datacenter = module.params.get('datacenter')
    server_name = module.params.get('server')
    server_id = module.params.get('server_id')

    # Check if the Server exists based on the supplied name
    try:
        if server_name is None and server_id is None:
            module.fail_json(msg='A server valid value for server or server_id is required')
        if server_id:
            server = client.get_server_by_id(server_id=server_id)
        else:
            server = client.get_server_by_name(datacenter=datacenter,
                                               network_domain_id=network_domain_id,
                                               name=server_name)
        if not server.get('id'):
            raise NTTMCPAPIException('No server found for {0}'.format(server_name or server_id))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not locate any existing server - {0}'.format(e))
    return server


def get_server_snapshot_service_info(module, client):
    """
    Get information on a Snapshot Service Plan

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: The Service Plan configuration
    """
    network_domain_id = get_network_domain_id(module, client)
    server = get_server(module, client, network_domain_id)

    return server.get('snapshotService', {})


def list_server_snapshot_info(module, client):
    """
    List all Snapshots for a server

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: The list of Snapshots that exist for a server
    """
    if not module.params.get('server_id'):
        network_domain_id = get_network_domain_id(module, client)
        server = get_server(module, client, network_domain_id)
        server_id = server.get('id')
    else:
        server_id = module.params.get('server_id')

    try:
        snapshots = client.list_snapshot(server_id)
        if not snapshots:
            module.fail_json(msg='Could not get a list of server snapshots')
    except (KeyError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not get a list of server snapshots - {0}'.format(e))

    return snapshots


def main():
    """
    Main function
    :returns: Snapshot Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=False, type='str'),
            plan=dict(required=False, type='str'),
            window=dict(required=False, default=None, type='int'),
            slots_available=dict(required=False, default=True, type='bool'),
            type=dict(required=False, default='window', choices=['window', 'server', 'plan', 'snapshot']),
            network_domain=dict(required=False, default=None, type='str'),
            server=dict(required=False, default=None, type='str'),
            server_id=dict(required=False, default=None, type='str')
        ),
        supports_check_mode=True
    )
    result = None
    return_data = {}
    return_type = 'window'
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

    snapshot_type = module.params.get('type')

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

    try:
        if snapshot_type == 'window':
            result = client.list_snapshot_windows(module.params.get('datacenter'),
                                                  module.params.get('plan'),
                                                  module.params.get('window'),
                                                  module.params.get('slots_available'))
        if snapshot_type == 'plan':
            return_type = 'snapshot_plan_info'
            result = client.list_snapshot_service_plans(module.params.get('plan'),
                                                        module.params.get('slots_available'))
        if snapshot_type == 'server':
            return_type = 'server_snapshot_info'
            result = get_server_snapshot_service_info(module, client)
        if snapshot_type == 'snapshot':
            return_type = 'snapshot_info'
            result = list_server_snapshot_info(module, client)

        if result:
            return_data = return_object(return_type)
            return_data[return_type] = result
            return_data['count'] = len(return_data.get(return_type))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve a list of Snapshot info - {0}'.format(e))

    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
