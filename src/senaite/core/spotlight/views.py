# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.SPOTLIGHT.
#
# SENAITE.CORE.SPOTLIGHT is free software: you can redistribute it and/or
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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import senaiteMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.spotlight.interfaces import ISpotlightSearchAdapter
from senaite.core.spotlight.interfaces import ISpotlightView
from senaite.jsonapi import add_route
from zope.component import getMultiAdapter
from zope.interface import implements


@add_route("/spotlight/search", "senaite.lims.spotlight", methods=["GET"])
def spotlight_search_route(context, request):
    """The spotlight search route
    """
    search_adapter = getMultiAdapter(
        (context, request), interface=ISpotlightSearchAdapter)
    return search_adapter()


class SpotlightView(BrowserView):
    """The spotlight search view just renders the template
    """
    implements(ISpotlightView)
    template = ViewPageTemplateFile("templates/spotlight.pt")
    viewlet = ViewPageTemplateFile("templates/spotlight_viewlet.pt")

    def __init__(self, context, request):
        request.set("disable_border", 1)
        self.context = context
        self.request = request
        self.css_class = "spotlight-view"
        self.css_style = "display:block;"
        self.viewlet = self.viewlet()

    def __call__(self):
        return self.template()
