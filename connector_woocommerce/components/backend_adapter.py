# -*- coding: utf-8 -*-
#
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import socket
import logging
import xmlrpclib

from datetime import datetime

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.connector.exception import NetworkRetryableError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from woocommerce import API
except ImportError:
    _logger.debug("Cannot import 'woocommerce'")


WOO_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class WooLocation(object):

    def __init__(self, location, consumer_key, consumre_secret, version):
        self._location = location
        self.consumer_key = consumer_key
        self.consumer_secret = consumre_secret
        self.version = version

    @property
    def location(self):
        location = self._location
        return location


class WooAPI(object):

    def __init__(self, location):
        """
        :param location: Woo location
        :type location: :class:`WooLocation`
        """
        self._location = location
        self._api = None

    @property
    def api(self):
#        if self._api is None:
#        api.__enter__()
        return self._api

    def __enter__(self):
        # we do nothing, api is lazy
        return self

    def __exit__(self, type, value, traceback):
        if self._api is not None:
            return
#            self._api.__exit__(type, value, traceback)

    def call(self, method, arguments):
        try:
            location = self._location._location
            cons_key = self._location.consumer_key
            sec_key = self._location.consumer_secret
            version = self._location.version or 'v3'
            api = API(url=location,
                        consumer_key=cons_key,
                        consumer_secret=sec_key,
                        version=version,
                        query_string_auth=True
                        )
            self._api = api
            if self._api:
                if isinstance(arguments, list):
                    while arguments and arguments[-1] is None:
                        arguments.pop()
                start = datetime.now()
                try:
                    if 'false' or 'true' or 'null'in \
                    self._api.get(method).content:
                        result = self._api.get(method).content.replace(
                            'false', 'False')
                        result = result.replace('true', 'True')
                        result = result.replace('null', 'False')
                        result = safe_eval(result)
                    else:
                        result = safe_eval(self._api.get(method).content)
                except:
                    _logger.error("api.call(%s, %s) failed", method, arguments)
                    raise
                else:
                    _logger.debug("api.call(%s, %s) returned %s in %s seconds",
                                  method, arguments, result,
                                  (datetime.now() - start).seconds)
                return result
        except (socket.gaierror, socket.error, socket.timeout) as err:
            raise NetworkRetryableError(
                'A network error caused the failure of the job: '
                '%s' % err)
        except xmlrpclib.ProtocolError as err:
            if err.errcode in [502,   # Bad gateway
                               503,   # Service unavailable
                               504]:  # Gateway timeout
                raise RetryableJobError(
                    'A protocol error caused the failure of the job:\n'
                    'URL: %s\n'
                    'HTTP/HTTPS headers: %s\n'
                    'Error code: %d\n'
                    'Error message: %s\n' %
                    (err.url, err.headers, err.errcode, err.errmsg))
            else:
                raise


class WooCRUDAdapter(AbstractComponent):
    """ External Records Adapter for Woo """

    _name = 'woo.crud.adapter'
    _inherit = ['base.backend.adapter', 'base.woo.connector']
    _usage = 'backend.adapter'

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """ Create a record on the external system """
        raise NotImplementedError

    def write(self, id, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, id):
        """ Delete a record on the external system """
        raise NotImplementedError

    def _call(self, method, arguments):
        try:
            woo_api = getattr(self.work, 'woo_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a woo_api attribute with a '
                'WooAPI instance to be able to use the '
                'Backend Adapter.'
            )
        return woo_api.call(method, arguments)


class GenericAdapter(AbstractComponent):

    _name = 'woo.adapter'
    _inherit = 'woo.crud.adapter'

    _woo_model = None
    _admin_path = None

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        return self._call('%s.search' % self._woo_model,
                          [filters] if filters else [{}])

    def read(self, id, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        arguments = []
        if attributes:
            # Avoid to pass Null values in attributes. Workaround for
            # is not installed, calling info() with None in attributes
            # would return a wrong result (almost empty list of
            # attributes). The right correction is to install the
            # compatibility patch on WooCommerce.
            arguments.append(attributes)
        return self._call('%s/' % self._woo_model + str(id), [])

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        return self._call('%s.list' % self._woo_model, [filters])

    def create(self, data):
        """ Create a record on the external system """
        return self._call('%s.create' % self._woo_model, [data])

    def write(self, id, data):
        """ Update records on the external system """
        return self._call('%s.update' % self._woo_model,
                          [int(id), data])

    def delete(self, id):
        """ Delete a record on the external system """
        return self._call('%s.delete' % self._woo_model, [int(id)])
