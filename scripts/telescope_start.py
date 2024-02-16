#!/usr/bin/python
"""
Example script for telescope startup
"""
import logging
import os

from ska_oso_scripting.objects import Telescope

LOG = logging.getLogger(__name__)
FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(level=logging.INFO, format=FORMAT)


def init(subarray_id):
    pass


def main(*args, **kwargs):
    """
    Start up telescope.
    """
    LOG.info(f'Running telescope start-up script in OS process {os.getpid()}')

    if args:
        LOG.warning('Got unexpected positional args: %s', args)
    if kwargs:
        LOG.warning('Got unexpected named args: %s', kwargs)

    telescope = Telescope()

    LOG.info(f'Starting telescope...')
    telescope.on()

    LOG.info('Telescope start-up script complete')

