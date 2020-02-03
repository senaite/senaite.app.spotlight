# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.spotlight.interfaces import ISpotlightView
from senaite.jsonapi import add_route
from zope.interface import implements
from zope.component import getMultiAdapter

from .interfaces import ISpotlightSearchAdapter


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
        self.placeholder = _("Search ...")
        self.viewlet = self.viewlet()

    def __call__(self):
        return self.template()
