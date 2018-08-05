# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.dcs import dcs_service
from openstack.dcs.v1 import dcsresource as _dcsresource
from openstack import resource2 as resource
from openstack import utils


class Instance(_dcsresource.Resource):

    base_path = "/instances"
    # base_path = '/instances'
    resource_key = 'instance'
    resources_key = 'instances'
    service = dcs_service.DCSService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_get = True
    allow_update = True
    allow_list = True

    # Properties
    id = resource.Body('id')
    description = resource.Body('description')
    engine = resource.Body('engine')
    engine_version = resource.Body('engine_version')
    capacity = resource.Body('capacity')
    no_password_access = resource.Body('no_password_access')
    password = resource.Body('password')
    access_user = resource.Body('access_user')
    vpc_id = resource.Body('vpc_id')
    security_group_id = resource.Body('security_group_id')
    subnet_id = resource.Body('subnet_id')
    available_zones = resource.Body('available_zones')
    product_id = resource.Body('product_id')
    instance_backup_policy = resource.Body('instance_backup_policy', type=dict)
    maintain_begin = resource.Body('maintain_begin')
    maintain_end = resource.Body('maintain_end')

    restorePoint = resource.Body("restorePoint", type=dict)

    _query_mapping = resource.QueryParameters(
        "start", "limit", "name", "id", "status", "includeFailure", "isExactMatchName",
    )

class InstanceDetails(_dcsresource.Resource):

    base_path = "/instances/%(instanceId)s"
    # base_path = '/instances'
    resource_key = 'instance'
    resources_key = 'instances'
    service = dcs_service.DCSService()
    instanceId = resource.URI('instanceId')

    # capabilities
    allow_get = True

    _query_mapping = resource.QueryParameters(
        "project_id", "instance_id",
    )
