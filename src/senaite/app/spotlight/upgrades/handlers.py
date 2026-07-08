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

from plone.registry.interfaces import IRegistry
from senaite.app.spotlight import logger
from senaite.app.spotlight.controlpanel import DEFAULT_CATALOGS
from senaite.app.spotlight.controlpanel import complete_catalog_row
from senaite.app.spotlight.controlpanel import complete_command_row
from zope.component import getUtility

PROFILE_ID = "profile-senaite.app.spotlight:default"

# Registry record holding the spotlight catalog rows
CATALOGS_RECORD = "senaite.app.spotlight.catalogs"

# Registry record holding the spotlight command rows
COMMANDS_RECORD = "senaite.app.spotlight.commands"


def to_2704(portal_setup):
    """Update to version 2.7.0

    Completes the persisted spotlight command rows and drops any leftover
    `<NO_VALUE>` sentinel cells (as done for the catalog rows), so the
    DataGrid renders the optional command cells (icon, permission,
    keywords) blank.

    :param portal_setup: The portal_setup tool
    """
    logger.info("Clean up spotlight command rows ...")
    registry = getUtility(IRegistry)
    rows = registry.get(COMMANDS_RECORD)
    if not rows:
        logger.info("No stored spotlight commands, nothing to do")
        return
    registry[COMMANDS_RECORD] = [
        complete_command_row(dict(row)) for row in rows]
    logger.info("Clean up spotlight command rows [DONE]")


def to_2703(portal_setup):
    """Update to version 2.7.0

    Backfills the new `show_for_clients` flag on installs that already
    persisted the spotlight catalog rows. Rows are matched by catalog id
    against the shipped defaults, so the lab-only catalogs (setup,
    worksheets, clients, contacts) become hidden from client contacts while
    every other catalog stays visible. Catalogs not shipped by default keep
    their value (or default to visible).

    Also completes every row and drops any leftover `<NO_VALUE>` sentinel
    cells (as the previous upgrade step did), so the DataGrid renders the
    optional cells blank.

    :param portal_setup: The portal_setup tool
    """
    logger.info("Set 'show_for_clients' on spotlight catalogs ...")
    registry = getUtility(IRegistry)
    rows = registry.get(CATALOGS_RECORD)
    if not rows:
        logger.info("No stored spotlight catalogs, nothing to do")
        return
    defaults = {row.get("catalog"): row.get("show_for_clients", True)
                for row in DEFAULT_CATALOGS}
    updated = []
    for row in rows:
        # complete the row and strip any "<NO_VALUE>" sentinel cells
        row = complete_catalog_row(dict(row))
        name = row.get("catalog")
        if name in defaults:
            # authoritative shipped visibility for the default catalogs
            row["show_for_clients"] = defaults[name]
        updated.append(row)
    registry[CATALOGS_RECORD] = updated
    logger.info("Set 'show_for_clients' on spotlight catalogs [DONE]")


def to_2702(portal_setup):
    """Update to version 2.7.0

    Backfills the spotlight catalog list for installs that already
    registered the control panel: existing rows are completed with the
    missing optional cells (so the DataGrid no longer renders the
    `<NO_VALUE>` marker) and the internal catalogs shipped as disabled
    rows are appended. Rows are matched by catalog id and existing
    customizations are preserved.

    :param portal_setup: The portal_setup tool
    """
    logger.info("Sync default spotlight catalog rows ...")
    registry = getUtility(IRegistry)
    catalogs = [complete_catalog_row(dict(row))
                for row in (registry.get(CATALOGS_RECORD) or [])]
    known = {row.get("catalog") for row in catalogs if row.get("catalog")}
    for row in DEFAULT_CATALOGS:
        name = row.get("catalog")
        if name and name not in known:
            catalogs.append(dict(row))
            known.add(name)
    registry[CATALOGS_RECORD] = catalogs
    logger.info("Sync default spotlight catalog rows [DONE]")


def to_2701(portal_setup):
    """Update to version 2.7.0

    Runs all import steps, which registers the spotlight control panel,
    registry records and resources for the React based search.

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")


def to_2700(portal_setup):
    """Update to version 2.7.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")


def to_2600(portal_setup):
    """Update to version 2.6.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")


def to_2500(portal_setup):
    """Update to version 2.5.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")


def to_2400(portal_setup):
    """Update to version 2.4.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")


def to_2300(portal_setup):
    """Update to version 2.3.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT ...")
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE APP SPOTLIGHT [DONE]")
