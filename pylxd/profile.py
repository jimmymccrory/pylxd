# Copyright (c) 2016 Canonical Ltd
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from pylxd import exceptions, model


class Profile(model.Model):
    """A LXD profile."""

    name = model.Attribute()
    description = model.Attribute()
    config = model.Attribute()
    devices = model.Attribute()

    @classmethod
    def get(cls, client, name):
        """Get a profile."""
        try:
            response = client.api.profiles[name].get()
        except exceptions.LXDAPIException as e:
            if e.response.status_code == 404:
                raise exceptions.NotFound()
            raise

        return cls(client, **response.json()['metadata'])

    @classmethod
    def all(cls, client):
        """Get all profiles."""
        response = client.api.profiles.get()

        profiles = []
        for url in response.json()['metadata']:
            name = url.split('/')[-1]
            profiles.append(cls(client, name=name))
        return profiles

    @classmethod
    def create(cls, client, name, config=None, devices=None):
        """Create a profile."""
        profile = {'name': name}
        if config is not None:
            profile['config'] = config
        if devices is not None:
            profile['devices'] = devices
        try:
            client.api.profiles.post(json=profile)
        except exceptions.LXDAPIException as e:
            raise exceptions.CreateFailed(e.response.json())

        return cls.get(client, name)

    @property
    def api(self):
        return self.client.api.profiles[self.name]

    def update(self):
        """Update the profile in LXD based on local changes."""
        try:
            marshalled = self.marshall()
        except AttributeError:
            raise exceptions.ObjectIncomplete()
        # The name property cannot be updated.
        del marshalled['name']

        self.api.put(json=marshalled)

    def rename(self, new):
        """Rename the profile."""
        raise NotImplementedError(
            'LXD does not currently support renaming profiles')
