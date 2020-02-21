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
module: vip_ssl
short_description: Create, Update and Delete VIP SSL Offload Profile Configuration
description:
    - Create, Update and Delete VIP SSL Offload Profile Configuration
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
            - The name of the SSL Offload Profile
        required: false
        type: str
    new_name:
        description:
            - The new name of the SSL Offload Profile. Used when modifying the name of an existing SSL Offload Profile.
        required: false
        type: str
    ciphers:
        description:
            - Ciphers needs to be a valid F5 Cipher string https://support.f5.com/csp/article/K13171
            - Example "DHE+AES:DHE+AES-GCM:RSA+AES:RSA+3DES:RSA+AES-GCM:DHE+3DES"
        required: false
        type: str
    id:
        description:
            - The UUID of the SSL Offload profile (can be used for deletion)
        required: false
        type: str
    certificate:
        description:
            - The certificate to use for the this SSL Offload Profile
        required: false
        type: dict
        suboptions:
            name:
                description:
                    - The name of the SSL certificate to upload/use
                required: true
                type: str
            path:
                description:
                    - The path to a valid SSL certificate file
                required: true
                type: str
            key_path:
                description:
                    - The path to the associated SSL certificate private key
                type: str
    chain:
        description:
            - The certificate chain to use for the this SSL Offload Profile
        required: false
        type: dict
        suboptions:
            name:
                description:
                    - The name of the SSL certificate chain to upload/use
                required: true
                type: str
            path:
                description:
                    - The path to a valid SSL certificate file
                required: true
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

  - name: Create an SSL Offload Profile
    vip_ssl:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_ssl_profile"
      description: "my ssl profile"
      certificate:
        name: "my_cert"
        description: "My Certificate"
        path: "/path/my_cert.pem"
        key_path: "/path/my_cert_key.pem"
      chain:
        name: "my_cert_chain"
        description: "My Certificate Chain"
        path: "/path/my_cert_chain.pem"
      ciphers: "DHE+AES:DHE+AES-GCM:RSA+AES:RSA+3DES:RSA+AES-GCM"
      state: present

  - name: Update an SLL Offload Profile - Update the name and change the certificate
    vip_ssl:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_ssl_profile"
      new_name: "my_ssl_profile_2"
      description: "my 2nd ssl profile"
      certificate:
        name: "my_cert_2"
        description: "My 2nd Certificate"
        path: "/path/my_cert_2.pem"
        key_path: "/path/my_cert_key_2.pem"
      chain:
        name: "my_cert_chain"
        description: "My Certificate Chain"
        path: "/path/my_cert_chain.pem"
      ciphers: "DHE+AES:DHE+AES-GCM:RSA+AES:RSA+3DES:RSA+AES-GCM"
      state: present

  - name: Delete an SSL Offload Profile - If this profile is the last associated profile with the cert and chain they will also be removed
    vip_ssl:
      region: na
      datacenter: NA9
      network_domain: "my_network_domain"
      name: "my_ssl_profile"
      state: absent
'''

RETURN = '''
data:
    description: The UUID of the SSL OffLoad profile being created or updated
    type: str
    sample: "b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae"
    returned: when state == present
msg:
    description: A useful message
    type: str
    returned: when state == absent
'''
from os import path
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, compare_json
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException
try:
    from OpenSSL import crypto
    HAS_OPENSSL = True
except ImportError:
    HAS_OPENSSL = False


def import_ssl_cert(module, client, network_domain_id):
    """
    Import an SSL certificate

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The network domain UUID
    :returns: Import result
    """
    cert_path = module.params.get('certificate').get('path')
    key_path = module.params.get('certificate').get('key_path')
    name = module.params.get('certificate').get('name')
    description = module.params.get('certificate').get('description')

    if not name:
        module.fail_json(msg='A valid certificate name is required')

    # Attempt to load the certificate and key and verify they are valid
    try:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_path).read())
        cert_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(key_path).read())
    except IOError as exc:
        module.fail_json(msg='The file {0} cannot be found'.format(exc.filename))
    except crypto.Error as exc:
        module.fail_json(msg='The certificate or key is invalid - {0}'.format(exc))

    try:
        import_result = client.import_ssl_cert(network_domain_id,
                                               name,
                                               description,
                                               crypto.dump_certificate(crypto.FILETYPE_PEM, cert),
                                               crypto.dump_privatekey(crypto.FILETYPE_PEM, cert_key))
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not import the SSL certificate - {0}'.format(exc))

    return import_result


def import_ssl_cert_chain(module, client, network_domain_id):
    """
    Import an SSL certificate chain

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The network domain UUID
    :returns: Import result
    """
    chain_path = module.params.get('chain').get('path')
    name = module.params.get('chain').get('name')
    description = module.params.get('chain').get('description')

    if not name:
        module.fail_json(msg='A valid certificate chain name is required')

    # Attempt to load the certificate and key and verify they are valid
    try:
        cert_chain = crypto.load_certificate(crypto.FILETYPE_PEM, open(chain_path).read())
    except IOError as exc:
        module.fail_json(msg='The file {0} cannot be found'.format(exc.filename))
    except crypto.Error as exc:
        module.fail_json(msg='The certificate chain is invalid - {0}'.format(exc))

    try:
        import_result = client.import_ssl_cert_chain(network_domain_id,
                                                     name, description,
                                                     crypto.dump_certificate(crypto.FILETYPE_PEM, cert_chain))
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not import the SSL certificate chain - {0}'.format(exc))

    return import_result


def create_ssl_offload_profile(module, client, network_domain_id, cert_id=None, cert_chain_id=None):
    """
    Create an SSL Profile

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The network domain UUID
    :arg cert_id: The SSL Profile certificate UUID
    :arg cert_chain_id: The SSL Profile certificate chain UUID
    """
    try:
        if cert_id is None:
            cert_id = client.list_ssl_cert(network_domain_id, module.params.get('certificate').get('name'))
        if cert_chain_id is None:
            cert_chain_id = client.list_ssl_cert_chain(network_domain_id, module.params.get('chain').get('name'))
        if cert_id is None:
            module.fail_json(msg='Could not find the SSL certificate with the name: {0}'.format(module.params.get('certificate').get('name')))
        elif cert_chain_id is None:
            module.fail_json(msg='Could not find the SSL certificate chain with the name: {0}'.format(module.params.get('chain').get('name')))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not find the SSL certificate or certificate chain - {0}'.format(exc))

    name = module.params.get('name')
    description = module.params.get('description')
    ciphers = module.params.get('ciphers')
    if name is None:
        module.fail_json(msg='A valid name is required')
    if ciphers is None:
        module.fail_json(msg='A valid cipher list is required')
    try:
        profile_result = client.create_ssl_offload_profile(network_domain_id, name, description, ciphers, cert_id, cert_chain_id)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not create the SSL Offload Profile - {0}'.format(exc))

    module.exit_json(changed=True, data=profile_result)


def update_ssl_offload_profile(module, client, profile, cert_id, cert_chain_id):
    """
    Update an SSL Profile

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg profile: The SSL Profile
    :arg cert_id: The SSL Profile certificate UUID
    :arg cert_chain_id: The SSL Profile certificate chain UUID
    """
    name = profile.get('name')
    if module.params.get('new_name'):
        name = module.params.get('new_name')
    try:
        client.update_ssl_offload_profile(profile.get('id'),
                                          module.params.get('new_name') or name,
                                          module.params.get('description'),
                                          module.params.get('ciphers') or profile.get('ciphers'),
                                          cert_id,
                                          cert_chain_id)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Failed to udpate the SSL Offload Profile {0}: {1}'.format(name, exc))
    module.exit_json(changed=True, data=profile.get('id'))


def delete_ssl_profile(module, client, network_domain_id=None, ssl_profile_id=None, cert=None, cert_chain=None):
    """
    Delete an SSL Profile

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The network domain UUID
    :arg ssl_profile_id: The SSL Profile UUID
    :arg cert: The SSL Profile certificate
    :arg cert_chain: The SSL Profile certificate chain
    """
    if ssl_profile_id is None:
        module.fail_json(msg='A valid SSL profile ID is required')

    try:
        client.remove_ssl('profile', ssl_profile_id)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not remove the SSL Offload Profile with the id: {0}: {1}'.format(ssl_profile_id, exc))

    try:
        ssl_profiles = client.list_vip_ssl(network_domain_id=network_domain_id, ssl_type='sslOffloadProfile')
        # If the SSL certificate and chain is no longer used by any other profiles remove them as well
        if not is_still_used('certificate', cert.get('name'), ssl_profiles):
            client.remove_ssl('certificate', cert.get('id'))
        if not is_still_used('chain', cert_chain.get('name'), ssl_profiles):
            client.remove_ssl('chain', cert_chain.get('id'))
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
        module.fail_json(msg='Could not remove the SSL certificate or certificate chain: {0}'.format(exc))

    module.exit_json(changed=True, msg='The SSL Offload Profile was successfully removed.')


def is_still_used(ssl_type, ssl_name, ssl_profiles):
    """
    Check if an SSL certificate/chain is still being used by an SSL Profile

    :arg ssl_type: The SSL certificate/chain type
    :arg ssl_name: The SSL certifcate/chain name
    :arg ssl_profiles: List of SSL profiles
    """
    for ssl_profile in ssl_profiles:
        if ssl_type == 'certificate':
            if ssl_profile.get('sslDomainCertificate').get('name') == ssl_name:
                return True
        elif ssl_type == 'chain':
            if ssl_profile.get('sslCertificateChain').get('name') == ssl_name:
                return True
    return False


def compare_ssl_profile(module, profile):
    """
    Compare the certificate object provided to the Ansible module arguments

    :arg module: The Ansible module instance
    :arg profile: The existing SSL profile
    """
    new_profile = deepcopy(profile)

    if module.params.get('new_name'):
        new_profile['name'] = module.params.get('new_name')
    if module.params.get('description'):
        new_profile['description'] = module.params.get('description')
    if module.params.get('ciphers'):
        new_profile['ciphers'] = module.params.get('ciphers')
    if module.params.get('certificate'):
        new_profile.get('sslDomainCertificate')['name'] = module.params.get('certificate').get('name')
    if module.params.get('chain'):
        new_profile.get('sslCertificateChain')['name'] = module.params.get('chain').get('name')

    compare_result = compare_json(new_profile, profile, None)
    # Implement Check Mode
    if module.check_mode:
        module.exit_json(data=compare_result)
    return compare_result.get('changes')


def verify_cert_chain_schema(module, client, network_domain_id):
    """
    Verify the certificate chain object provided in the Ansible module arguments

    :arg module: The Ansible module instance
    :arg client: The CC API instance
    :arg network_domain_id: The UUID of the Cloud Network Domain
    """
    cert_chains = []
    cert_chain = module.params.get('chain')
    if not cert_chain.get('name'):
        module.fail_json(msg='A valid certificate chain name is required')
    # If a name was provided check if an existing cert already exists
    try:
        cert_chains = client.list_vip_ssl(network_domain_id, 'sslCertificateChain', cert_chain.get('name'))
    except NTTMCPAPIException:
        pass
    if not cert_chain.get('path'):
        if not cert_chains:
            module.fail_json(msg='A valid path to the certificate chain file is required')
    else:
        if not path.isfile(cert_chain.get('path')):
            module.fail_json(msg='Could not find the certificate chain file at: {0}'.format(cert_chain.get('path')))


def verify_cert_schema(module, client, network_domain_id):
    """
    Verify the certificate object provided in the Ansible module arguments

    :arg module: The Ansible module instance
    :arg client: The CC API instance
    :arg network_domain_id: The UUID of the Cloud Network Domain
    """
    certs = []
    cert = module.params.get('certificate')
    if not cert.get('name'):
        module.fail_json(msg='A valid certificate name is required')
    # If a name was provided check if an existing cert already exists
    try:
        certs = client.list_vip_ssl(network_domain_id, 'sslDomainCertificate', cert.get('name'))
    except NTTMCPAPIException:
        pass
    if not cert.get('path'):
        if not certs:
            module.fail_json(msg='A valid name or path to the certificate file is required')
    else:
        if not path.isfile(cert.get('path')):
            module.fail_json(msg='Could not find the certificate file at: {0}'.format(cert.get('path')))
    if not cert.get('key_path'):
        if not certs:
            module.fail_json(msg='A valid path to the certificate key file is required')
    else:
        if not path.isfile(cert.get('key_path')):
            module.fail_json(msg='Could not find the certificate key file at: {0}'.format(cert.get('key_path')))


def main():
    """
    Main function

    :returns: SSL Profile Information
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
            chain=dict(required=False, default=None, type='dict'),
            certificate=dict(required=False, default=None, type='dict'),
            new_name=dict(required=False, default=None, type='str'),
            ciphers=dict(required=False, default=None, type='str'),
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
    name = module.params.get('name')
    profile = cert = new_cert = cert_chain = new_cert_chain = None

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

    # Verify SSL certificate  and certificate chain schema
    if state == 'present':
        verify_cert_schema(module, client, network_domain_id)
        verify_cert_chain_schema(module, client, network_domain_id)

        # Check if the SSL certificate and chain already exist
        try:
            certs = client.list_vip_ssl(network_domain_id=network_domain_id, ssl_type='sslDomainCertificate',
                                        name=module.params.get('certificate').get('name'))
            if len(certs) == 1:
                new_cert = certs[0]
                new_cert_id = new_cert.get('id')
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
            module.fail_json(msg='Failed to get a list of current SSL certificates: {0}'.format(exc))
        try:
            cert_chains = client.list_vip_ssl(network_domain_id=network_domain_id, ssl_type='sslCertificateChain',
                                              name=module.params.get('chain').get('name'))
            if len(cert_chains) == 1:
                new_cert_chain = cert_chains[0]
                new_cert_chain_id = new_cert_chain.get('id')
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
            module.fail_json(msg='Failed to get a list of current SSL certificate chains: {0}'.format(exc))

    # Check if the SSL Profile already exists
    if name:
        try:
            profiles = client.list_vip_ssl(network_domain_id=network_domain_id, ssl_type='sslOffloadProfile', name=name)
            if len(profiles) == 1:
                if profiles[0].get('name'):
                    profile = profiles[0]
                    cert = client.get_vip_ssl(ssl_type='sslDomainCertificate',
                                              ssl_id=profiles[0].get('sslDomainCertificate').get('id'))
                    cert_chain = client.get_vip_ssl(ssl_type='sslCertificateChain',
                                                    ssl_id=profiles[0].get('sslCertificateChain').get('id'))
        except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as exc:
            module.fail_json(msg='Failed getting a list of SSL Offload Profiles to check against - {0}'.format(exc))

    if state == 'present':
        # Implement Check Mode
        if module.check_mode and not profile:
            module.exit_json(msg='A new SSL Offload Profile will be created')
        # Handle new certificates and certificate chains first
        if not new_cert:
            new_cert_id = import_ssl_cert(module, client, network_domain_id)
        if not new_cert_chain:
            new_cert_chain_id = import_ssl_cert_chain(module, client, network_domain_id)
        if not profile:
            create_ssl_offload_profile(module, client, network_domain_id, new_cert_id, new_cert_chain_id)
        else:
            if compare_ssl_profile(module, profile):
                update_ssl_offload_profile(module, client, profile, new_cert_id, new_cert_chain_id)
            else:
                module.exit_json(data=profile.get('id'))
    elif state == 'absent':
        if not profile:
            module.exit_json(msg='The SSL Profile was not found. Nothing to remove.')
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='The SSL Offload Profile with ID {0} will be deleted'.format(profile.get('id')))
        delete_ssl_profile(module, client, network_domain_id, profile.get('id'), cert, cert_chain)


if __name__ == '__main__':
    main()
