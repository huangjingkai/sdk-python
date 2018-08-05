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


from openstack import exceptions
from openstack import resource2 as resource
from openstack import utils


class Resource(resource.Resource):

    def _get_custom_url(self, session, url):
        key = (self.service.service_type, self.service.interface)

        if key in session.endpoint_cache:
            base_url = session.endpoint_cache[key]
        else:
            base_url = session.get_endpoint(
                interface=self.service.interface,
                service_type=self.service.service_type)

        # IAM only returns redis base url, as we need to hack
        # this to support both hw redis and openstack redis
        # provide custom url per resource type
        custom_url = utils.urljoin(base_url, self._version_str,
                                   session.get_project_id(), url)
        return custom_url

    # overwrite resource2._prepare_request as maas requires header
    # to have Content-type
    def _prepare_request(self, requires_id=True, prepend_key=False):
        body = self._body.dirty
        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}

        headers = self._header.dirty

        headers.update({'Content-type': 'application/json',
                        'X-Language': 'en-us'})

        uri = self.base_path % self._uri.attributes
        if requires_id:
            if self.id is None:
                raise exceptions.InvalidRequest(
                    "Request requires an ID but none was found")

            uri = utils.urljoin(uri, self.id)

        return resource._Request(uri, body, headers)

    # overwrite resource2._prepare_request as redis requires header
    def get(self, session, requires_id=True):
        if not self.allow_get:
            raise exceptions.MethodNotSupported(self, "get")
        request = self._prepare_request(requires_id=requires_id)
        endpoint_override = self.service.get_endpoint_override()
        if endpoint_override is None:
            request.uri = self._get_custom_url(session, request.uri)
        else:
            endpoint_override = self._get_custom_override(endpoint_override)

        response = session.get(request.uri, endpoint_filter=self.service,
                               endpoint_override=endpoint_override,
                               headers=request.headers)

        self._translate_response(response)
        return self

    @classmethod
    def list(cls, session, paginated=False, **params):
        more_data = True
        query_params = cls._query_mapping._transpose(params)
        uri = cls.base_path % params

        # Notes: smn requires to have Content-type Header, but there's no way
        # to update header in list method, rewrite it, most are copied from
        # resource2.py.list
        headers = {"Accept": "application/json",
                   "Content-type": "application/json"}

        while more_data:
            endpoint_override = cls.service.get_endpoint_override()
            resp = session.get(uri, endpoint_filter=cls.service,
                               endpoint_override=endpoint_override,
                               headers=headers,
                               params=query_params)

            if not resp:
                more_data = False

            return resp.json()

    def create(self, session, prepend_key=True):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        endpoint_override = self.service.get_endpoint_override()
        uri = self.base_path % self._uri.attributes
        headers = self._header.dirty
        body = self._body.dirty

        headers.update({'Content-type': 'application/json',
                        'X-Language': 'en-us'})

        if self.put_create:
            response = session.put(uri, endpoint_filter=self.service,
                                   endpoint_override=endpoint_override,
                                   json=body, headers=headers)
        else:
            response = session.post(uri, endpoint_filter=self.service,
                                    endpoint_override=endpoint_override,
                                    json=body, headers=headers)

        return response.json()

        # self._translate_response(response)
        # return self

    def update(self, session, prepend_key=True, has_body=True):
        """Update the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource update request.
                            Default to True.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        # The id cannot be dirty for an update
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to update.
        if not any([self._body.dirty, self._header.dirty]):
            return self

        if not self.allow_update:
            raise exceptions.MethodNotSupported(self, "update")

        request = self._prepare_request(prepend_key=prepend_key)

        endpoint_override = self.service.get_endpoint_override()
        if endpoint_override is None:
            request.uri = self._get_custom_url(session, request.uri)
        else:
            endpoint_override = self._get_custom_override(endpoint_override)

        if self.patch_update:
            response = session.patch(request.uri, endpoint_filter=self.service,
                                     endpoint_override=endpoint_override,
                                     json=request.body,
                                     headers=request.headers)
        else:
            response = session.put(request.uri, endpoint_filter=self.service,
                                   endpoint_override=endpoint_override,
                                   json=request.body, headers=request.headers)

        self._translate_response(response, has_body=has_body)
        return self

    def delete(self, session):
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, "delete")

        request = self._prepare_request()

        endpoint_override = self.service.get_endpoint_override()
        if endpoint_override is None:
            request.uri = self._get_custom_url(session, request.uri)
        else:
            endpoint_override = self._get_custom_override(endpoint_override)

        response = session.delete(request.uri, endpoint_filter=self.service,
                                  endpoint_override=endpoint_override,
                                  headers={"Accept": ""})

        self._translate_response(response, has_body=False)
        return self