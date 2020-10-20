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
module: vip_ssl_info
short_description: List/Get VIP SSL Configuration
description:
    - List/Get VIP SSL Configuration
    - It is quicker to use the option "id" to locate the SSL configuration if the UUID is known rather than search by name
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
            - The datacenter name
        required: true
        default: null
        type: str
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        type: str
        default: null
    id:
        description:
            - The UUID of the node
        required: false
        type: str
        default: null
    name:
        description:
            - The name of the node
        required: false
        type: str
        default: null
    type:
        description:
            - The type of SSL entity to search for
        required: false
        default: certificate
        type: str
        choices:
            - certificate
            - chain
            - profile
notes:
    - Requires NTT Ltd. MCP account/credentials
    - MCP SSL Certificates, Chains, Profile documentation https://docs.mcp-services.net/x/aIJk
    - List of F5 ciphers https://support.f5.com/csp/article/K13171
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

  - name: List all SSL certificates for a Network Domain
    vip_ssl_info:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"

  - name: List all SSL Chains for a Network Domain
    vip_ssl_info:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      type: chain

  - name: Get a specific SSL Profile by ID
    vip_ssl_info:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      type: profile
      id: bbc866b0-2f13-44b4-8339-49890f10dc3c

  - name: Get a specific SSL Profile by name
    vip_ssl_info:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      type: profile
      name: "My_SSL_Profile"
'''

RETURN = '''
data:
    description: Dictionary of the vlan
    returned: success
    type: complex
    contains:
        ssl_certificate:
            description: List of SSL Certificates
            returned: when type == 'certificate' (default)
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
                description:
                    description: SSL certificate description
                    type: str
                    sample: "My Cert"
                createTime:
                    description: The creation date of the SSL certificate
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                name:
                    description: The SSL certificate display name
                    type: str
                    sample: "my_cert"
                expiryTime:
                    description: The expiry date of the SSL certificate
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                id:
                    description:  The UUID of the SSL certificate
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        ssl_chain:
            description: List of SSL Chain
            returned: when type == 'chain' (default)
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
                description:
                    description: SSL chain description
                    type: str
                    sample: "My Cert"
                createTime:
                    description: The creation date of the SSL chain
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                name:
                    description: The SSL chain display name
                    type: str
                    sample: "my_chain"
                expiryTime:
                    description: The expiry date of the SSL chain
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                id:
                    description:  The UUID of the SSL chain
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
        ssl_profile:
            description: SSL Profile Object
            returned: when type == 'profile' (default)
            type: complex
            contains:
                networkDomainId:
                    description: The UUID of the Cloud Network Domain
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                sslDomainCertificate:
                    description: List of SSL Certificates
                    type: complex
                    contains:
                        expiryTime:
                            description: The expiry date of the SSL certificate
                            type: str
                            sample: "2019-01-14T11:12:31.000Z"
                        id:
                            description:  The UUID of the SSL certificate
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The SSL certificate display name
                            type: str
                            sample: "my_cert"
                name:
                    description: The name of the SSL Offload Profile
                    type: str
                    sample: "my_ssl_profile"
                ciphers:
                    description: Cipher needs to be a valid F5 Cipher string - https://support.f5.com/csp/article/K13171
                    type: str
                    sample: "DHE+AES:DHE+AES-GCM:RSA+AES:RSA+3DES:RSA+AES-GCM:DHE+3DES"
                id:
                    description: The UUID of the SSL Offload Profile
                    type: str
                    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                datacenterId:
                    description: The MCP ID
                    type: str
                    sample: NA9
                state:
                    description: The operational state of the SSL Offload Profile
                    type: str
                    sample: "NORMAL"
                sslCertificateChain:
                    description: The optional SSL certificate chain
                    type: complex
                    contains:
                        expiryTime:
                            description: The expiry date of the SSL chain
                            type: str
                            sample: "2019-01-14T11:12:31.000Z"
                        id:
                            description:  The UUID of the SSL chain
                            type: str
                            sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
                        name:
                            description: The SSL chain display name
                            type: str
                            sample: "my_chain"
                createTime:
                    description: The creation date of the SSL chain
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function

    :returns: SSL Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            id=dict(default=None, required=False, type='str'),
            type=dict(default='certificate', required=False, choices=['certificate', 'chain', 'profile']),
            name=dict(default=None, required=False, type='str')
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
    object_type = module.params.get('type')
    api_object_type = None
    name = module.params.get('name')
    return_data = return_object('ssl_{0}'.format(object_type))

    # Assign the actual CC API attribute name for the object type
    if object_type == 'certificate':
        api_object_type = 'sslDomainCertificate'
    elif object_type == 'chain':
        api_object_type = 'sslCertificateChain'
    elif object_type == 'profile':
        api_object_type = 'sslOffloadProfile'

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

    try:
        if object_id:
            return_data['ssl_{0}'.format(object_type)] = client.get_vip_ssl(api_object_type, object_id)
        else:
            return_data['ssl_{0}'.format(object_type)] = client.list_vip_ssl(network_domain_id, api_object_type, name)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not find the SSL object(s): {0}'.format(exc))
    return_data['count'] = len(return_data['ssl_{0}'.format(object_type)])
    module.exit_json(data=return_data)


if __name__ == '__main__':
    main()
