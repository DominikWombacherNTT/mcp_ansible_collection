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
module: snapshot_service
short_description: Enable/Disable and Update the Snapshot Service on a server
description:
    - Enable/Disable and Update the Snapshot Service on a server
    - When disabling snapshot replication on a server it can take 2-4 hours for this process to finish even if though
    - the tasks returns immediately. Disabling the snapshot service on a server requires that snapshot replication is
    - already disabled.
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
        required: true
        type: str
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: false
        type: str
    network_domain_id:
        description:
            - The ID of a Cloud Network Domain.
        required: false
        type: str
    server:
        description:
            - The name of a server to enable Snapshots on
        required: false
        type: str
    server_id:
        description:
            - The UUID of a server to enable Snapshots on. Takes precendence over a server name
        required: false
        type: str
    plan:
        description:
            - The name of a desired Service Plan. Use snapshot_info to get a list of valid plans.
        required: false
        type: str
    window:
        description:
            - The starting hour for the snapshot window (24 hour notation). Use snapshot_info to find a window.
        required: false
        type: int
    take_snapshot:
        description:
            - Whether to initiate a manual snapshot
        required: false
        default: false
        type: bool
    replication:
        description:
            - Enable replication of snapshots for this server to the target datacenter/MCP
            - Value should be the target datacenter ID within the same GEO e.g. NA12
            - This is an optional parameter that should only be specified if replication is required
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
    - Introduction to Cloud Server Snapshots - https://docs.mcp-services.net/x/DoBk
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

  - name: Enable Snapshots at 8am
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain_id: my_network_domain_uuid
      name: My_Server
      plan: ONE_MONTH
      window: 8

  - name: Enable Snapshots at 8am
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      plan: ONE_MONTH
      window: 8
      state: present

  - name: Enable Snapshots at 8am and enable replication
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      plan: ONE_MONTH
      window: 8
      replication: NA12

  - name: Update Snapshot config on a server
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      plan: TWELVE_MONTH
      window: 10

  - name: Add replication to the service
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      replication: NA12

  - name: Disable replication only
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      replication: NA12
      state: absent

  - name: Disable Snapshots Completely
    snapshot_service:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: My_Server
      state: absent
'''
RETURN = '''
msg:
    description: Status of the operation
    returned: always
    type: str
'''

from time import sleep
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, compare_json
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def enable_snapshot(module, client, server_id, plan, window_id, replication_mcp, take_snapshot):
    """
    Enable the Snapshot Service on a server

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :arg server_id: The UUID of the server
    :arg plan: The service plan to use (e.g. ONE_MONTH)
    :arg window_id: The UUID of the snapshot Window
    :arg replicaiton_mcp: The ID of the replication MCP
    :arg take_snapshot: Whether to initiate a manual snapshot
    :returns: Message on exit
    """
    try:
        result = client.enable_snapshot_service(False, server_id, plan, window_id, replication_mcp, take_snapshot)
        if result.get('responseCode') == 'OK' or result.get('responseCode') == 'IN_PROGRESS':
            '''
            # Check if replication is required
            if module.params.get('replication') is not None:
                result = client.enable_snapshot_replication(server_id, module.params.get('replication'))
                if result.get('responseCode') != 'OK':
                    module.fail_json(warning='Failed to enable replication, however Snapshots have been successfully '
                                     'enabled'
            '''
            module.exit_json(changed=True, msg='Snapshots successfully enabled')
        else:
            module.fail_json(msg='Failed to enable Snapshosts: {0}'.format(str(result)))
    except (AttributeError, KeyError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed to enable Snapshosts: {0}'.format(e))


def update_snapshot(module, client, server_id, plan, window_id):
    """
    Enable the Snapshot Service on a server

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :arg server_id: The UUID of the server
    :arg plan: The service plan to use (e.g. ONE_MONTH)
    :arg window_id: The UUID of the snapshot Window
    :returns: N/A
    """
    result = ''
    try:
        if plan and window_id:
            result = client.enable_snapshot_service(True, server_id, plan, window_id)
        if result.get('responseCode') != 'OK':
            module.fail_json(msg='Failed to update Snapshost Service configuration: {0}'.format(str(result)))
    except (AttributeError, KeyError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed to update Snapshost Service configuration: {0}'.format(e))


def enable_replication(module, client, server_id, replication_dc):
    """
    Enable just replication on the Snapshot Service for a server

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :arg server_id: The UUID of the server
    :arg replication_dc: The datacenter ID for the replication target
    :returns: N/A
    """
    try:
        result = client.enable_snapshot_replication(server_id, replication_dc)
        if result.get('responseCode') != 'OK':
            raise NTTMCPAPIException(result.get('message', 'Generic Failure'))
    except NTTMCPAPIException as e:
        module.fail_json(msg='Failed to disable snapshot replication - {0}'.format(e))


def disable_replication(module, client, server_id):
    """
    Disable just replication on the Snapshot Service for a server

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :arg server_id: The UUID of the server
    :returns: N/A
    """
    state = 'NORMAL'
    actual_state = None
    set_state = False
    wait_poll_interval = 5
    wait_time = 120
    time = 0
    try:
        result = client.disable_snapshot_replication(server_id)
        if result.get('responseCode') != 'IN_PROGRESS':
            raise NTTMCPAPIException(result.get('message', 'Generic Failure'))
        # Wait for the service replication state to become Normal before proceeding
        while not set_state and time < wait_time:
            try:
                server = client.get_server_by_id(server_id=server_id)
            except NTTMCPAPIException as e:
                module.warn(warning='Failed to check the server - {0}'.format(e))
            actual_state = server.get('snapshotService', {}).get('state')
            if actual_state != state:
                wait_required = True
            else:
                wait_required = False

            if wait_required:
                sleep(wait_poll_interval)
                time = time + wait_poll_interval
            else:
                set_state = True
    except NTTMCPAPIException as e:
        module.fail_json(msg='Failed to disable snapshot replication - {0}'.format(e))


def disable_snapshot(module, client, server_id):
    """
    Disable the Snapshot Service on a server

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :arg server_id: The UUID of the server
    :returns: N/A
    """
    try:
        result = client.disable_snapshot_service(server_id)
        if result.get('responseCode') != 'OK':
            module.fail_json(msg='Failed to disable Snapshosts: {0}'.format(str(result)))
    except (AttributeError, KeyError, NTTMCPAPIException) as e:
        module.fail_json(msg='Failed to disable Snapshosts: {0}'.format(e))


def compare_snapshot(module, snapshot_config):
    """
    Compare the existing Snapshot config to the provided arguments

    :arg module: The Ansible module instance
    :arg snapshot_config: The dict containing the existing Snapshot config to compare to
    :returns: Tuple of any differences between the the Snapshot configs, service is item 0 and replication is item 1
    """
    service_change = replication_change = False
    new_config = deepcopy(snapshot_config)
    if module.params.get('plan'):
        new_config['servicePlan'] = module.params.get('plan')
    if module.params.get('replication'):
        new_config['replicationTargetDatacenterId'] = module.params.get('replication')
    if module.params.get('window'):
        new_config['window'] = {
            'dayOfWeek': '',
            'startHour': module.params.get('window')
        }
        if module.params.get('plan') in ['ONE_MONTH', 'THREE_MONTH', 'TWELVE_MONTH']:
            new_config['window']['dayOfWeek'] = 'DAILY'

    compare_result = compare_json(new_config, snapshot_config, None)
    # determine if the change is a service or replication or both change
    consolidate_changes = compare_result.get('added')
    consolidate_changes.update(compare_result.get('updated'))
    if 'servicePlan' in consolidate_changes or 'window' in consolidate_changes:
        service_change = True
    if 'replicationTargetDatacenterId' in consolidate_changes:
        replication_change = True
    # Implement Check Mode
    if module.check_mode:
        module.exit_json(data=compare_result)
    return (service_change, replication_change)


def get_window_id(module, client):
    """
    Search for the Snapshot Window and return the UUID

    :arg module: The Ansible module instance
    :arg client: The CC API provider instance
    :returns: The Window UUID
    """
    window_id = None
    try:
        result = client.list_snapshot_windows(module.params.get('datacenter'),
                                              module.params.get('plan'),
                                              module.params.get('window'),
                                              module.params.get('slots_available'))
        window_id = result[0].get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve the required Snapshot Window - {0}'.format(e))
    return window_id


def main():
    """
    Main function
    :returns: Snapshot Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=False, type='str'),
            network_domain_id=dict(required=False, type='str'),
            server=dict(required=False, type='str'),
            server_id=dict(required=False, type='str'),
            plan=dict(required=False, default=None, type='str'),
            window=dict(required=False, default=None, type='int'),
            replication=dict(required=False, default=None, type='str'),
            take_snapshot=dict(required=False, default=False, type='bool'),
            state=dict(default='present', choices=['present', 'absent'])
        ),
        supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

    state = module.params.get('state')
    datacenter = module.params.get('datacenter')
    network_domain_name = module.params.get('network_domain')
    server_name = module.params.get('server')
    server_id = module.params.get('server_id')
    plan = module.params.get('plan')
    window_id = None
    network_domain_id = module.params.get('network_domain_id')
    take_snapshot = module.params.get('take_snapshot')

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
    if server_id is None and network_domain_id is None:
        try:
            network = client.get_network_domain_by_name(name=network_domain_name, datacenter=datacenter)
            network_domain_id = network.get('id')
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
            module.fail_json(msg='Could not find the Cloud Network Domain: {0}'.format(e))

    # Check if the Server exists based on the supplied name
    try:
        if server_name is None and server_id is None:
            module.fail_json(msg='A valid value for server or server_id is required')
        if server_id:
            server = client.get_server_by_id(server_id=server_id)
        else:
            server = client.get_server_by_name(datacenter=datacenter,
                                               network_domain_id=network_domain_id,
                                               name=server_name)
        if not server.get('id'):
            raise NTTMCPAPIException('No server object found for {0}'.format(server_name or server_id))
        server_id = server.get('id')
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not locate any existing server - {0}'.format(e))

    if state == 'present':
        # Check for required arguments
        if (module.params.get('plan') is None or module.params.get('window') is None) and module.params.get('replication') is None:
            module.fail_json(msg='plan and window are required arguments')
        # Attempt to find the Window for the specified Service Plan
        if not module.check_mode and (module.params.get('window') or module.params.get('plan')):
            window_id = get_window_id(module, client)
        if not server.get('snapshotService'):
            if module.check_mode:
                module.exit_json(msg='Input verified, Snapshots can be enabled for the server')
            enable_snapshot(module, client, server_id, plan, window_id, module.params.get('replication'), take_snapshot)
        else:
            result = compare_snapshot(module, server.get('snapshotService'))
            if True in result:
                if result[0]:
                    update_snapshot(module, client, server_id, plan, window_id)
                if result[1]:
                    enable_replication(module, client, server_id, module.params.get('replication'))
                module.exit_json(changed=True, msg='Snapshot Service configuration has been successfully updated')
            else:
                module.exit_json(msg='No update required.')
    elif state == 'absent':
        if not server.get('snapshotService'):
            module.exit_json(msg='Snapshots are not currently configured for this server')
        if module.check_mode:
            module.exit_json(msg='The Snapshot service and all associated snapshots will be removed from this server')
        if module.params.get('replication'):
            disable_replication(module, client, server_id)
        else:
            disable_snapshot(module, client, server_id)
        module.exit_json(msg='Snapshot replication successfully disabled')


if __name__ == '__main__':
    main()
