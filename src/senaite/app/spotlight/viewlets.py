# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.APP.SPOTLIGHT.
#
# SENAITE.APP.SPOTLIGHT is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from AccessControl import getSecurityManager
from bika.lims import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.app.spotlight.controlpanel import get_config
from senaite.app.spotlight.controlpanel import get_state_suggestions
from senaite.core.permissions import ManageSenaite


class SpotlightViewlet(ViewletBase):
    """The spotlight search viewlet renders the React mount node on all pages
    """
    index = ViewPageTemplateFile("templates/spotlight_viewlet.pt")

    def update(self):
        pass

    def can_manage(self, portal):
        """Check if the current user may manage the spotlight settings
        """
        sm = getSecurityManager()
        return bool(sm.checkPermission(ManageSenaite, portal))

    def allowed_command(self, command, portal):
        """Check if the current user is allowed to see the command

        Commands without a `permission` are always shown. Otherwise the
        permission is checked against the portal for the current user.
        """
        permission = command.get("permission")
        if not permission:
            return True
        return bool(getSecurityManager().checkPermission(permission, portal))

    def get_config_json(self):
        """Return the resolved spotlight configuration as a JSON string
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        config = get_config()
        config["commands"] = [
            command for command in config["commands"]
            if self.allowed_command(command, portal)
        ]
        # ship the available states per catalog for the "is:<state>"
        # autocomplete suggestions (active/inactive plus workflow states)
        for catalog in config["catalogs"]:
            catalog["states"] = get_state_suggestions(catalog["name"])
        config["portal_url"] = portal_url
        config["api_url"] = "{}/@@API/spotlight/search".format(portal_url)
        config["commands_url"] = "{}/@@API/spotlight/commands".format(
            portal_url)
        config["can_manage"] = self.can_manage(portal)
        config["settings_url"] = "{}/@@spotlight-controlpanel".format(
            portal_url)
        config["search_url"] = "{}/@@spotlight-search".format(portal_url)
        return json.dumps(config)
