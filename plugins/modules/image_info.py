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
module: image_info
short_description: Get available server images information
description:
    - Get available server images information
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
            - The datacenter name e.g NA9
        required: false
        type: str
    id:
        description:
            - The UUID of the image, supports wildcard matching with "*" e.g. "*ffff*"
        required: false
        type: str
    name:
        description:
            - The name of the infrastructure entity, supports wildcard matching with "*" e.g. "*Centos*"
        required: false
        type: str
    family:
        description:
            - The OS family name of the infrastructure entity
        required: false
        type: str
        choices:
            - UNIX
            - WINDOWS
    customer_image:
        description:
            - Is this a customer import image
        required: false
        type: bool
        default: false
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests>=2.21.0
'''

EXAMPLES = '''
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: Get a list of Operating Systems in NA12
    image_info:
      region: na
      datacenter: NA12
    register: image
    tags:
      - list

  - name: Get a list of Operating Systems in NA12 by wildcard name
    image_info:
      region: na
      datacenter: NA12
      name: "*Centos*"

  - name: Get a list of Windows Operating Systems in NA12 by wildcard name
    image_info:
      region: na
      datacenter: NA12
      name: "*WINDOWS*"

  - name: Get a specific image in NA12 by ID
    image_info:
      region: na
      datacenter: NA12
      id: 112b7faa-ffff-ffff-ffff-dc273085cbe4
'''

RETURN = '''
data:
    description: dict of returned Objects
    type: complex
    returned: success
    contains:
        count:
            description: The total count of found/returned objects
            returned: success
            type: int
            sample: 5
        image:
            description: A list of images
            returned: success
            type: complex
            contains:
                cpu:
                    description: The default CPU specifications for the image
                    type: complex
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
                createTime:
                    description: The creation date of the image
                    type: str
                    sample: "2019-01-14T11:12:31.000Z"
                datacenterId:
                    description: The MCP id for this image
                    type: str
                    sample: "NA9"
                description:
                    description: The description for the image
                    type: str
                    sample: "My OS Image"
                guest:
                    description: Custom VM attributes for the image
                    type: complex
                    contains:
                        operatingSystem:
                            description: The operating system attributes for this image
                            type: complex
                            contains:
                                displayName:
                                    description: The name of the OS
                                    type: str
                                    sample: "CENTOS7/64"
                                family:
                                    description: The OS family e.g. UNIX or WINDOWS
                                    type: str
                                    sample: "UNIX"
                                id:
                                    description: OS ID
                                    type: str
                                    sample: "CENTOS764"
                                osUnitsGroupId:
                                    description: The OS billing group
                                    type: str
                                    sample: "CENTOS"
                        osCustomization:
                            description: Does this OS support guest OS cusomtizations
                            type: bool
                            sample: true
                id:
                    description: OS ID
                    type: str
                    sample: "CENTOS764"
                memoryGb:
                    description: The default memory setting for this image in GB
                    type: int
                    sample: 4
                name:
                    description: The common name for the Image
                    type: str
                    sample: "CentOS 7 64-bit 2 CPU"
                osImageKey:
                    description: Internal image identifier
                    type: str
                    sample: "T-CENT-7-64-2-4-10"
                scsiController:
                    description: SCSI controller and disk configuration for the image
                    type: complex
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
                softwareLabel:
                    description: List of associated labels
                    type: list
                    sample:
                        - "MSSQL2012R2E"
                tag:
                    description: List of associated tags
                    type: complex
                    contains:
                        tagKeyId:
                            description: GUID of the tag
                            type: str
                            sample: "112b7faa-ffff-ffff-ffff-dc273085cbe4"
                        tagKeyName:
                            description: Human readable key name
                            type: str
                            sample: "Owner"
                        value:
                            description: The value of the key
                            type: str
                            sample: "Someone"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def get_image(module, client):
    """
    List images filtered by optional parameters from the Ansible arguments
    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg network_domain_id: The UUID of the network domain
    :returns: List of image objects
    """
    return_data = return_object('image')
    image_id = module.params['id']
    image_name = module.params['name']
    os_family = module.params['family']
    datacenter = module.params['datacenter']
    customer_image = module.params['customer_image']

    try:
        if customer_image:
            result = client.list_customer_image(datacenter_id=datacenter, image_id=image_id, image_name=image_name, os_family=os_family)
        else:
            result = client.list_image(datacenter_id=datacenter, image_id=image_id, image_name=image_name, os_family=os_family)
    except NTTMCPAPIException as exc:
        module.fail_json(msg='Could not get a list of images - {0}'.format(exc))
    try:
        if customer_image:
            return_data['count'] = result['totalCount']
            return_data['image'] = result['customerImage']
        else:
            return_data['count'] = result['totalCount']
            return_data['image'] = result['osImage']
    except KeyError:
        pass

    module.exit_json(data=return_data)


def main():
    """
    Main function
    :returns: Image Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            region=dict(default='na', type='str'),
            datacenter=dict(required=False, type='str'),
            id=dict(required=False, type='str'),
            name=dict(required=False, type='str'),
            family=dict(required=False, choices=['UNIX', 'WINDOWS']),
            customer_image=dict(default=False, type='bool')
        ),
        supports_check_mode=True
    )

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Could not load the user credentials')

    # Create the API client
    try:
        client = NTTMCPClient(credentials, module.params.get('region'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=e.msg)

    get_image(module=module, client=client)


if __name__ == '__main__':
    main()
