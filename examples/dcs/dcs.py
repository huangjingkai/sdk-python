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

"""
Managing dms
"""
from openstack import connection
import sys,os

# utils.enable_logging(debug=False,stream=sys.stdout)

# create connection
username = "huangjingkai"
password = "XX"
projectId = "0d5949b3f9844b9a8e9cf9fd3e92348c"    # tenant ID
userDomainId = "c231b5325e7c4b12ac90fb84472c45e2"    # user account ID
auth_url = "https://iam.cn-south-1.myhuaweicloud.com/v3"    # endpoint url

conn = connection.Connection(auth_url=auth_url,
                              user_domain_id=userDomainId,
                              project_id=projectId,
                              username=username,
                              password=password)

os.environ.setdefault(
    'OS_DCS_ENDPOINT_OVERRIDE',
    'https://dcs.cn-south-1.myhuaweicloud.com/v1.0/%(project_id)s')


os.environ.setdefault(
    'OS_RDS_ENDPOINT_OVERRIDE',
    'https://rds.cn-south-1.myhuaweicloud.com/v1.0/%(project_id)s')

os.environ.setdefault(
    'OS_DMS_ENDPOINT_OVERRIDE',
    'https://dms.cn-south-1.myhuaweicloud.com/v1.0/%(project_id)s')

# REDIS
def createRedisInstance(conn):
    query = {
        "name": "dcs-04",
        "description": "python sdk test",
        "engine":"Redis",
        "engine_version":"3.0.7",
        "capacity":2,
        "password":"1qaz@WSX",
        "vpc_id":"b1b12250-8f38-422e-bd62-b30e5a955a21",
        "security_group_id":"abef8ced-5cf4-4a8e-80ea-59707c65ccf9",
        "subnet_id":"c9cfcb94-7448-4ed3-83f7-55bf8eb7e38e",
        "available_zones":["34f5ff4865cf4ed6b270f15382ebdec5"],
        "product_id":"00301-31100-0--0"
    }

    instance=conn.dcs.create_instance(**query)
    print(instance)

def listRedisInstance(conn):
    query = {
        "start": 1,
        "limit": 10,
        "includeFailure": True,
        "isExactMatchName": False
    }
    instance=conn.dcs.instances(**query)
    print(instance)

def listRedisInstanceDetail(conn):
    query = {
        "instance_id": "d9efa3be-6302-4168-8ea2-4adb8264a36d"
    }
    instance=conn.dcs.instance_details(**query)
    print(instance)

createRedisInstance(conn)
listRedisInstance(conn)
listRedisInstanceDetail(conn)