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

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SpotlightViewlet(ViewletBase):
    """The spotlight search viewlet renders on all pages
    """
    index = ViewPageTemplateFile("templates/spotlight_viewlet.pt")

    def __init__(self, context, request, view, manager):
        super(SpotlightViewlet, self).__init__(context, request, view, manager)
        self.css_class = "spotlight-overlay"
        self.css_style = "display:none;"

    def update(self):
        pass
