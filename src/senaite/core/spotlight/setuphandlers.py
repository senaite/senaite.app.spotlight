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

from senaite.core.spotlight import logger


def setup_handler(context):
    """Generic setup handler
    """

    if context.readDataFile('senaite.core.spotlight.txt') is None:
        return

    logger.info("SENAITE.CORE.SPOTLIGHT setup handler [BEGIN]")
    portal = context.getSite()  # noqa
    logger.info("SENAITE.CORE.SPOTLIGHT setup handler [DONE]")


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE.CORE.SPOTLIGHT install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-senaite.core.spotlight:default"
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    logger.info("SENAITE.CORE.SPOTLIGHT install handler [DONE]")


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE.CORE.SPOTLIGHT uninstall handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-senaite.core.spotlight:uninstall"
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    logger.info("SENAITE.CORE.SPOTLIGHT uninstall handler [DONE]")
