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
from zope.component import getUtility

PROFILE_ID = "profile-senaite.app.spotlight:default"

# Registry record holding the spotlight catalog rows
CATALOGS_RECORD = "senaite.app.spotlight.catalogs"


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
