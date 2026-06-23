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

import re

from bika.lims import api
from bika.lims.api.security import check_permission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View

# Meta type of a Dexterity factory type information
DX_FTI_META_TYPE = "Dexterity FTI"


def prettify_title(title):
    """Insert spaces at camelCase boundaries for titles that have none

    e.g. "AnalysisCategory" -> "Analysis Category". Titles that already
    contain a space (e.g. "Analysis Service" or a translated title) are
    returned unchanged.
    """
    title = api.safe_unicode(title)
    if not title or u" " in title:
        return title
    spaced = re.sub(u"([a-z0-9])([A-Z])", u"\\1 \\2", title)
    spaced = re.sub(u"([A-Z]+)([A-Z][a-z])", u"\\1 \\2", spaced)
    return spaced


def get_setup_folders():
    """Return the /setup and bika_setup configuration folders
    """
    folders = []
    for getter in (api.get_senaite_setup, api.get_bika_setup):
        folder = getter()
        if folder is not None:
            folders.append(folder)
    return folders


def can_access_setup():
    """Whether the current user may access the setup at all

    Acts as a gate so that users without access to the setup (e.g. clients)
    never see setup related commands and never trigger the enumeration.
    """
    return any(check_permission(View, folder)
               for folder in get_setup_folders())


def get_add_url(folder, type_id, dexterity):
    """Build the add URL for a type within a folder
    """
    folder_url = api.get_url(folder)
    if dexterity:
        return "{}/++add++{}".format(folder_url, type_id)
    return "{}/createObject?type_name={}".format(folder_url, type_id)


def can_add(folder, fti):
    """Check if the current user may add the given type in the folder
    """
    add_permission = getattr(fti, "add_permission", None)
    if add_permission:
        return check_permission(add_permission, folder)
    # AT types without an explicit add permission: fall back to the folder
    return check_permission(ModifyPortalContent, folder)


def to_add_command(folder, fti):
    """Build a "create new X" command for an addable type
    """
    type_id = fti.getId()
    dexterity = getattr(fti, "meta_type", "") == DX_FTI_META_TYPE
    return {
        "id": "add-{}".format(type_id),
        "title": u"New {}".format(prettify_title(fti.Title())),
        "icon": "fas fa-plus",
        "url": get_add_url(folder, type_id, dexterity),
        "keywords": ["new", "add", "create"],
    }


def get_setup_add_commands():
    """Lazily build "create new X" commands from the addable types of every
    /setup and bika_setup configuration folder

    Permission filtered and de-duplicated by type. Looked up on demand (when
    the command palette is opened) so the object wakeup cost is only paid when
    the palette is actually used.
    """
    # gate the whole lookup: users without setup access (e.g. clients) get
    # nothing and do not trigger the enumeration
    if not can_access_setup():
        return []
    commands = []
    seen = set()
    for parent in get_setup_folders():
        for folder in parent.objectValues():
            allowed = getattr(folder, "allowedContentTypes", None)
            if allowed is None:
                continue
            for fti in allowed():
                type_id = fti.getId()
                if type_id in seen:
                    continue
                if not can_add(folder, fti):
                    continue
                seen.add(type_id)
                commands.append(to_add_command(folder, fti))
    return sorted(commands, key=lambda c: (c["title"] or "").lower())


def get_dynamic_commands():
    """Return all dynamically looked-up command palette actions
    """
    return get_setup_add_commands()
