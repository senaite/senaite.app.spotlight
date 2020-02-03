# -*- coding: utf-8 -*-

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
