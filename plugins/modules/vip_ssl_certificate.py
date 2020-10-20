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
module: vip_ssl_certificate
short_description: Create and Delete VIP SSL Certificate/Chain
description:
    - Create and Delete VIP SSL Certificate/Chain
    - Certificates/Chains cannot be updated or removed while still associated with an SSL Offload Profile
    - Adding certifications/chains can also be done a single step as part of creating an SSL Offload Profile using
    - vip_ssl
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
        type: str
    description:
        description:
            - The description of the Cloud Network Domain
        required: false
        type: str
    network_domain:
        description:
            - The name of a Cloud Network Domain
        required: true
        type: str
    name:
        description:
            - The name of the SSL certificate/chain name
        required: false
        type: str
    id:
        description:
            - The UUID of the SSL certificate/chain  (can be used for deletion)
        required: false
        type: str
    type:
        description:
            -The type of SSL certificate (certificate or chain)
        required: false
        type: str
        default: certificate
        choices:
            - certificate
            - chain
    path:
        description:
            - The path to a valid SSL certificate (including certificate chain) file
        required: false
        type: str
    key_path:
        description:
            - The path to the associated SSL certificate private key
            - Only required type == 'certificate' (default)
        required: false
        type: str
    state:
        description:
            - The action to be performed
        default: present
        type: str
        choices:
            - present
            - absent
notes:
    - Requires NTT Ltd. MCP account/credentials
    - MCP SSL Certificates/Chains/Profile documentation https://docs.mcp-services.net/x/aIJk
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

  - name: Import a SSL certificate
    vip_ssl_certificate:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_cert"
      description: "my ssl cert"
      type: certificate
      path: "/path/my_cert.pem"
      key_path: "/path/my_cert_key.pem"
      state: present

  - name: Import a SSL chain
    vip_ssl_certificate:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_chain"
      description: "my ssl chain"
      type: chain
      path: "/path/my_chain.pem"
      state: present

  - name: Delete an SSL Certificate
    vip_ssl_certificate:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_ssl_cert"
      state: absent
'''

RETURN = '''
data:
    description: The UUID of the SSL Certifcate/Chain being created or updated
    type: str
    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
    returned: when state == present
msg:
    description: A useful message
    type: str
    returned: when state == absent
'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException
try:
    from OpenSSL import crypto
    HAS_OPENSSL = True
except ImportError:
    HAS_OPENSSL = False


def import_ssl_cert(module, client, network_domain_id):
    """
    Deletes a SSL certificate/chain
    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    """
    cert_path = module.params.get('path')
    key_path = module.params.get('key_path')
    name = module.params.get('name')
    description = module.params.get('description')
    ssl_type = module.params.get('type')

    if not name:
        module.fail_json(msg='A valid SSL certificate/chain name is required')

    # Attempt to load the certificate and key and verify they are valid
    try:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_path).read())
        if ssl_type == 'certificate':
            cert_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(key_path).read())
    except IOError as exc:
        module.fail_json(msg='The file {0} cannot be found'.format(exc.filename))
    except crypto.Error as exc:
        module.fail_json(msg='The certificate or key is invalid - {0}'.format(exc))

    try:
        if ssl_type == 'certificate':
            import_result = client.import_ssl_cert(network_domain_id,
                                                   name,
                                                   description,
                                                   crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('UTF-8'),
                                                   crypto.dump_privatekey(crypto.FILETYPE_PEM, cert_key).decode('UTF-8'))
        elif ssl_type == 'chain':
            import_result = client.import_ssl_cert_chain(network_domain_id,
                                                         name, description,
                                                         crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('UTF-8'))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not import the SSL certificate/chain - {0}'.format(exc))

    module.exit_json(changed=True, data=import_result)


def delete_ssl_cert(module, client, ssl_id):
    """
    Deletes a SSL certificate/chain
    :arg module: The Ansible module instance
    :arg ssl_id: The UUID of the SSL certificate/chain
    """
    if not ssl_id:
        module.fail_json(msg='A valid SSL certificate/chain ID is required')
    try:
        client.remove_ssl(module.params.get('type'), ssl_id)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not remove the SSL certificate or certificate chain: {0}'.format(exc))


def is_used(ssl_type, ssl_name, ssl_profiles):
    """
    Checks if an SSL certificate/chain (ssl_name) is still used by any SSL profiles
    :arg ssl_type: The type of SSL certificate/chain
    :arg ssl_name: The name of the SSL certificate/chain
    :arg ssl_profiles: A list of SSL Profiles
    :returns: a list of associated SSL profiles
    """
    associated_ssl_profiles = []
    try:
        for ssl_profile in ssl_profiles:
            if ssl_type == 'certificate':
                if ssl_profile.get('sslDomainCertificate').get('name') == ssl_name:
                    associated_ssl_profiles.append(ssl_profile.get('name'))
            elif ssl_type == 'chain':
                if ssl_profile.get('sslCertificateChain').get('name') == ssl_name:
                    associated_ssl_profiles.append(ssl_profile.get('name'))
        return associated_ssl_profiles
    except AttributeError:
        return associated_ssl_profiles


def main():
    """
    Main function
    :returns: SSL Certificate Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            datacenter=dict(required=True, type='str'),
            network_domain=dict(required=True, type='str'),
            id=dict(required=False, default=None, type='str'),
            name=dict(required=False, default=None, type='str'),
            description=dict(required=False, default=None, type='str'),
            type=dict(required=False, default='certificate', choices=['certificate', 'chain']),
            path=dict(required=False, default=None, type='str'),
            key_path=dict(required=False, default=None, type='str'),
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
    cert = None
    associated_ssl_profiles = []

    # Check Imports
    if not HAS_OPENSSL:
        module.fail_json(msg='Missing Python module: pyOpenSSL')

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Error: Could not load the user credentials')

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

    # Check if the SSL certificate already exists
    try:
        if module.params.get('id'):
            if module.params.get('type') == 'certificate':
                cert = client.get_vip_ssl('sslDomainCertificate', module.params.get('id'))
            elif module.params.get('type') == 'chain':
                cert = client.get_vip_ssl('sslCertificateChain', module.params.get('id'))
        else:
            if module.params.get('type') == 'certificate':
                certs = client.list_vip_ssl(network_domain_id=network_domain_id,
                                            name=module.params.get('name'),
                                            ssl_type='sslDomainCertificate')
            elif module.params.get('type') == 'chain':
                certs = client.list_vip_ssl(network_domain_id=network_domain_id,
                                            name=module.params.get('name'),
                                            ssl_type='sslCertificateChain')
            if len(certs) == 1:
                cert = certs[0]
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not get a list of existing SSL certificates/chains to check against - {0}'.format(exc))

    # Check if the cert is associated with any SSL Offload profiles. SSL certs cannot be updated or removed while still associated with an Offload Profile
        try:
            ssl_profiles = client.list_vip_ssl(network_domain_id=network_domain_id, ssl_type='sslOffloadProfile')
            associated_ssl_profiles = is_used(module.params.get('type'), module.params.get('name'), ssl_profiles)
            if associated_ssl_profiles:
                module.fail_json(msg='Cannot operate on the SSL {0} {1} as it is still associated with the following'
                                 'SSL Offload profiles: {2}'.format(module.params.get('type'), module.params.get('name'),
                                                                    associated_ssl_profiles))
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
            module.fail_json(msg='Failed getting a list of SSL Offload Profiles to check against - {0}'.format(exc))

    if state == 'present':
        if not cert:
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='The new SSL certificate will be imported')
            import_ssl_cert(module, client, network_domain_id)
        else:
            # Implement Check Mode
            if module.check_mode:
                module.exit_json(msg='An SSL certificate already exists, the old certificate will be removed and the new one imported')
            delete_ssl_cert(module, client, cert.get('id'))
            import_ssl_cert(module, client, network_domain_id)
    elif state == 'absent':
        if not cert:
            module.exit_json(msg='The SSL certificate/chain was not found. Nothing to remove.')
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='The SSL certificate with ID {0} will be removed'.format(cert.get('id')))
        delete_ssl_cert(module, client, cert.get('id'))
        module.exit_json(changed=True, msg='The SSL certificate/chain was successfully removed.')


if __name__ == '__main__':
    main()
