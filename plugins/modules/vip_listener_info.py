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
module: vip_listener_info
short_description: List/Get VIP Virtual Listeners
description:
    - List/Get VIP Virtual Listeners
    - It is quicker to use the option "id" to locate the VIP Virtual Listener if the UUID is known
    - rather than search by name
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
            - The name of a Cloud Network Domain
        required: true
        type: str
    id:
        description:
            - The UUID of the VIP Virtual Listener
        required: false
        type: str
    name:
        description:
            - The name of the VIP Virtual Listener
        required: false
        type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
    - https://docs.mcp-services.net/x/7gMk
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

  - name: List All VIP Virtual Listener
    vip_listener_info:
      region: na
      datacenter: NA9
      network_domain: my_network_domain

  - name: Get a specific VIP Virtual Listener by name
    vip_listener_info:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      name: my_listener

  - name: Get a specific VIP Virtual Listener by ID
    vip_listener_info:
      region: na
      datacenter: NA9
      network_domain: my_network_domain
      id: 56cfa8ec-c178-47ff-98fd-b5580ca33778
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
        vip_listener:
            description: VIP Virtual Listener
            returned: success
            type: complex
            contains:
                datacenterId:
                    description: The MCP ID
                    type: str
                    sample: NA9
                networkDomainId:
                    description: The UUID of the Cloud Network Domain
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                protocol:
                    description: Which protocol will be associated with the Virtual Listener
                    type: str
                    sample: TCP
                description:
                    description: The description for the Virtual Listener
                    type: str
                    sample: "My Virtual Listener"
                listenerIpAddressability:
                    description: Is the Virtual Listener a public or private IPv4 address
                    type: str
                    sample: PRIVATE_RFC1918
                sslOffloadProfile:
                    description: The SSL Offload Profile associated with this Virtual Listener (if any)
                    type: complex
                    contains:
                        id:
                            description: The UUID of the SSL Offload Profile
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the SSL Offload Profile
                            type: str
                            sample: "my_ssl_profile"
                type:
                    description:
                        - The virtual listener type is used to both specify how the load balancer should handle
                        - traffic and what features/options can be assigned.
                    type: str
                    sample: Standard
                sourcePortPreservation:
                    description:
                        - Identifies how the port of the source traffic will be treated when sending
                        - connections to the pool member.
                    type: str
                    sample: Preserve
                enabled:
                    description: Should the Virtual Listener be enabled
                    type: bool
                persistenceProfile:
                    description:
                        - Provides a method for ensuring that traffic from a client is sent to the same
                        - server in a pool based on an attribute of the connection.
                    type: complex
                    contains:
                        id:
                            description: The UUID of the persistence profile
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the persistence profile
                            type: str
                            sample: CCDEFAULT.SourceAddress
                fallbackPersistenceProfile:
                    description: The secondary persistence profile
                    type: complex
                    contains:
                        id:
                            description: The UUID of the persistence profile
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the persistence profile
                            type: str
                            sample: CCDEFAULT.Tcp
                id:
                    description: The UUID of the Virtual Listener
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                connectionRateLimit:
                    description:
                        - The amount of new connections permitted every second. Should be an
                        - integer between 1 and 4,000.
                    type: int
                    sample: 4000
                optimizationProfile:
                    description:
                        - For certain combinations of Virtual Listener type and protocol,
                        - it is possible to specify an additional optimization profile.
                    type: str
                    sample: TCP
                irule:
                    description:
                        - Custom configured rules that are applied to Virtual Servers to perform a wide
                        - array of actions.
                    type: list
                    contains:
                        id:
                            description: The UUID of the irule
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The name of the irule
                            type: str
                            sample: "CCDEFAULT.IpProtocolTimers"
                state:
                    description: The operation state of the Virtual Listener
                    type: str
                    sample: NORMAL
                connectionLimit:
                    description:
                        - The maximum number of simultaneous connections permitted on the Node.
                        - Should be an integer between 1 and 100,000
                    type: int
                    sample: 100000
                listenerIpAddress:
                    description: The IPv4 address the Virtual Listener is configured to listen on
                    type: str
                    sample: 10.0.0.10
                createTime:
                    description: The creation date of the Virtual Listener
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                pool:
                    description: dict containing the VIP Pool
                    type: complex
                    contains:
                        name:
                            description: The VIP Pool display name
                            type: str
                            sample: "my_pool"
                        loadBalanceMethod:
                            description: Defines how the Pool will handle load balancing
                            type: str
                            sample: "Round Robin"
                        slowRampTime:
                            description: This allows a Server to slowly ramp up connection
                            type: int
                            sample: 10
                        healthMonitor:
                            description:
                                - The procedure that the load balancer uses to verify that the VIP Pool is
                                - considered healthy and available for load balancing
                            type: complex
                            contains:
                                id:
                                    description: The UUID of the Health Monitor
                                    type: str
                                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                                name:
                                    description: The Health Monitor display name
                                    type: str
                                    sample: CCDEFAULT.Tcp
                        serviceDownAction:
                            description:
                                - When a Pool Member fails to respond to a Health Monitor, the system marks
                                - that Pool Member down and removes any persistence entries associated with
                                - the Pool Member
                            type: str
                            sample: "RESELECT"
                        id:
                            description:  The UUID of the VIP Pool
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                name:
                    description: The name of the Virtual Listener
                    type: str
                    sample: "my_listener"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: VIP Listener Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            id=dict(default=None, required=False, type='str'),
            name=dict(default=None, required=False, type='str'),
        ),
        supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))
    network_domain_name = module.params.get('network_domain')
    datacenter = module.params.get('datacenter')
    object_id = module.params.get('id')
    name = module.params.get('name')
    return_data = return_object('vip_listener')

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
    if object_id:
        try:
            return_data['vip_listener'] = client.get_vip_listener(object_id)
            module.exit_json(data=return_data)
        except NTTMCPAPIException as exc:
            module.fail_json(msg='Could not find the Virtual Listener {0}: {1}'.format(object_id, exc))
    else:
        return_data['vip_listener'] = client.list_vip_listener(network_domain_id, name)
        return_data['count'] = len(return_data.get('vip_listener'))
        module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
