# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SpotlightViewlet(ViewletBase):
    """The spotlight search viewlet renders on all pages
    """
    index = ViewPageTemplateFile("templates/spotlight_viewlet.pt")

    def __init__(self, context, request, view, manager):
        super(SpotlightViewlet, self).__init__(context, request, view, manager)
        self.css_class = "spotlight-overlay"

    def update(self):
        pass
