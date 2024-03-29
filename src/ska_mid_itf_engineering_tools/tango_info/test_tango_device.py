#!/usr/bin/python
"""Test devices from Tango database."""

import logging
import os
import time
from typing import Any

import tango


class TestTangoDevice:
    """Test a Tango device."""

    def __init__(self, logger: logging.Logger, device_name: str):
        """
        Get going.

        :param logger: logging handle
        :param device_name: Tango device name
        """
        self.logger = logger
        self.adminMode: int | None = None
        self.attribs = []
        self.cmds = []
        self.logger.info("Connect device proxy to %s", device_name)
        try:
            self.dev: tango.DeviceProxy = tango.DeviceProxy(device_name)
        except tango.ConnectionFailed as terr:
            print(f"[FAILED] {device_name} connection failed")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            self.dev = None
        except tango.DevFailed as terr:
            print(f"[FAILED] {device_name} device failed")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            self.dev = None
        if self.dev is not None:
            try:
                self.adminMode = self.dev.adminMode
                print(f"[  OK  ] admin mode {self.adminMode}")
            except AttributeError as terr:
                self.adminMode = None
                self.logger.debug(terr)
            self.dev_name = self.dev.name()
            self.attribs = sorted(self.dev.get_attribute_list())
            self.cmds = self.dev.get_command_list()
        self.dev_status: str | None = None
        self.dev_state: int | None = None
        self.simMode: int | None = None

    def get_admin_mode(self) -> int | None:
        """
        Read attribute for admin mode.

        :return: attribute value
        """
        if "adminMode" not in self.attribs:
            print(f"[ WARN ] {self.dev_name} does not have an adminMode attribute")
            self.adminMode = None
            return None
        try:
            self.adminMode = self.dev.adminMode
            print(f"[  OK  ] admin mode {self.adminMode}")
        except AttributeError as terr:
            print("[FAILED] could not read admin mode")
            self.logger.debug(terr)
            self.adminMode = None
        return self.adminMode

    def get_simulation_mode(self) -> int | None:
        """
        Read attribute for simulation mode.

        :return: attribute value
        """
        if "simulationMode" not in self.attribs:
            print(f"[ WARN ] {self.dev_name} does not have a simulationMode attribute")
        try:
            self.simMode = self.dev.simulationMode
            print(f"[  OK  ] simulation mode {self.simMode}")
        except AttributeError as terr:
            print("[FAILED] could not read simulation mode")
            self.logger.debug(terr)
            self.simMode = None
        return self.simMode

    def set_simulation_mode(self, dev_sim: int | None) -> int | None:
        """
        Set attribute for simulation mode.

        :param dev_sim: attribute value
        :return: error condition
        """
        if "simulationMode" not in self.attribs:
            print(f"[ WARN ] {self.dev_name} does not have a simulationMode attribute")
        try:
            self.dev.simulationMode = dev_sim
            self.simMode = self.dev.simulationMode
            print(f"[  OK  ] simulation mode set to {self.simMode}")
        except AttributeError as terr:
            print(f"[FAILED] could not set simulation mode to {dev_sim}")
            self.logger.debug(terr)
            self.simMode = None
            return 1
        if dev_sim != self.simMode:
            print(f"[FAILED] simulation mode should be {dev_sim} but is {self.simMode}")
        return 0

    def check_device(self) -> bool:
        """
        Check that device is online.

        :return: online condition
        """
        try:
            self.dev.ping()
            print(f"[  OK  ] {self.dev_name} is online")
        except Exception as terr:
            print(f"[FAILED] {self.dev_name} is not online")
            self.logger.debug(terr)
            return False
        return True

    def show_device_attributes(self, show: bool = False) -> None:
        """
        Display number and names of attributes.

        :param show: flag to print names
        """
        print(f"[  OK  ] {self.dev_name} has {len(self.attribs)} attributes")
        if show:
            for attrib in self.attribs:
                print(f"\t{attrib}")

    def read_device_attributes(self) -> None:
        """Read all attributes of this device."""
        self.logger.debug("Read attribute %s values", self.dev_name)
        print(f"[  OK  ] {self.dev_name} read {len(self.attribs)} attributes")
        for attrib in sorted(self.attribs):
            time.sleep(2)
            try:
                attrib_value = self.dev.read_attribute(attrib).value
                print(f"[  OK  ] {self.dev_name} attribute {attrib} : {attrib_value}")
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} attribute {attrib} could not be read")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)

    def show_device_commands(self, show: bool = False) -> None:
        """
        Display number and names of commands.

        :param show: flag to print names
        """
        print(f"[  OK  ] {self.dev_name} has {len(self.cmds)} commands")
        if show:
            for cmd in sorted(self.cmds):
                print(f"\t{cmd}")

    def admin_mode_off(self) -> None:
        """Turn admin mode off."""
        if self.adminMode is None:
            return
        if self.adminMode == 1:
            self.logger.info("Turn device admin mode off")
            try:
                self.dev.adminMode = 0
                self.adminMode = self.dev.adminMode
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} admin mode could not be turned off")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
                return
            self.adminMode = self.dev.adminMode
        print(f"[  OK  ] {self.dev_name} admin mode set to off, now ({self.adminMode})")

    def device_status(self) -> int | None:
        """
        Print device status.

        :return: device state
        """
        if "Status" not in self.cmds:
            print(f"[FAILED] {self.dev.dev_name} does not have Status command")
        if "State" not in self.cmds:
            print(f"[FAILED] {self.dev.dev_name} does not have State command")
            return None
        self.dev_status = self.dev.Status()
        self.dev_state = self.dev.State()
        print(f"[  OK  ] {self.dev_name} state : {self.dev_state} ({self.dev_state:d})")
        print(f"[  OK  ] {self.dev_name} status : {self.dev_status}")
        return self.dev_state

    def device_on(self) -> int:
        """
        Turn this device on.

        :return: error condition
        """
        self.logger.debug("Turn device %s on", self.dev_name)
        if "On" not in self.cmds:
            print(f"[FAILED] {self.dev_name} does not have On command")
            return 1
        cmd_cfg = self.dev.get_command_config("On")
        if cmd_cfg.in_type_desc == "Uninitialised":
            try:
                dev_on = self.dev.On()
                print(f"[  OK  ] {self.dev_name} turned on, now {dev_on}")
                return 1
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be turned on")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
        else:
            try:
                dev_on = self.dev.On([])
                print(f"[  OK  ] {self.dev_name} turned on, now {dev_on}")
                return 1
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be turned on (device failed)")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
                return 1
            except TypeError as terr:
                print(
                    f"[FAILED] {self.dev_name} could not be turned on"
                    f" (parameter type should be {cmd_cfg.in_type_desc})"
                )
                self.logger.debug(terr)
                return 1
        return 0

    def device_off(self) -> int:
        """
        Turn this device off.

        :return: error condition
        """
        self.logger.debug("Turn device %s off", self.dev_name)
        if "Off" not in self.cmds:
            print(f"[FAILED] {self.dev_name} does not have Off command")
            return 1
        cmd_cfg = self.dev.get_command_config("Off")
        if cmd_cfg.in_type_desc == "Uninitialised":
            try:
                dev_off = self.dev.Off()
                print(f"[  OK  ] {self.dev_name} turned off, now {dev_off}")
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be turned off")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
                return 1
        else:
            try:
                dev_off = self.dev.Off([])
                print(f"[  OK  ] {self.dev_name} turned off, now {dev_off}")
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be turned off")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
                return 1
        return 0

    def device_standby(self) -> int:
        """
        Set this device to standby mode.

        :return: error condition
        """
        self.logger.debug("Set device %s on standby", self.dev_name)
        if "Standby" not in self.cmds:
            print(f"[FAILED] {self.dev.dev_name} does not have Standby command")
            return 1
        cmd_cfg = self.dev.get_command_config("Standby")
        if cmd_cfg.in_type_desc == "Uninitialised":
            try:
                dev_standby = self.dev.Standby()
                print(f"[  OK  ] {self.dev_name} switched to standby, now {dev_standby}")
                return 0
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be switched to standby")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
        else:
            try:
                dev_standby = self.dev.Standby([])
                print(f"[  OK  ] {self.dev_name} switched to standby, now {dev_standby}")
                return 0
            except tango.DevFailed as terr:
                print(f"[FAILED] {self.dev_name} could not be switched to standby")
                print(f"[FAILED] {terr.args[0].desc.strip()}")
                self.logger.debug(terr)
        return 1

    def admin_mode_on(self) -> None:
        """Turn admin mode on."""
        self.logger.info("Turn device admin mode on")
        try:
            self.dev.adminMode = 1
            self.adminMode = self.dev.adminMode
        except tango.DevFailed as terr:
            print(f"[FAILED] {self.dev_name} admin mode could not be turned on")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            return
        print(f"[  OK  ] {self.dev_name} admin mode turned on, now ({self.adminMode})")

    def set_admin_mode(self, admin_mode: int) -> int:
        """
        Change admin mode.

        :param admin_mode: new value
        :return: error condition
        """
        self.logger.info("Set device admin mode to %d", admin_mode)
        try:
            self.dev.adminMode = admin_mode
            self.adminMode = self.dev.adminMode
        except tango.DevFailed as terr:
            print(f"[FAILED] {self.dev_name} admin mode could not be changed")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            return 1
        if self.adminMode != admin_mode:
            print(
                f"[FAILED] {self.dev_name} admin mode is {self.adminMode}"
                f" but should be {admin_mode}"
            )
            return 1
        print(f"[  OK  ] {self.dev_name} admin mode set to ({self.adminMode})")
        return 0

    def test_admin_mode(self, dev_admin: int) -> int:
        """
        Test admin mode.

        :param dev_admin: new value
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        # Read admin mode
        self.get_admin_mode()
        if self.adminMode is not None:
            self.set_admin_mode(dev_admin)
        return 0

    def test_off(self, dev_sim: int | None) -> int:
        """
        Test that device can be turned off.

        :param dev_sim: flag for hardware simulation.
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        if dev_sim is not None:
            self.set_simulation_mode(dev_sim)
        self.show_device_attributes()
        self.show_device_commands()
        # Read admin mode
        self.get_admin_mode()
        # Read state
        self.device_status()
        # Turn device off
        self.device_off()
        # Turn on admin mode
        self.admin_mode_on()
        # Read state
        self.device_status()
        return 0

    def test_on(self, dev_sim: int | None) -> int:
        """
        Test that device can be turned on.

        :param dev_sim: flag for hardware simulation.
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        if dev_sim is not None:
            self.set_simulation_mode(dev_sim)
        self.show_device_attributes()
        self.show_device_commands()
        # Read admin mode, turn off
        self.get_admin_mode()
        self.admin_mode_off()
        # Turn device on
        init_state = self.device_status()
        # pylint: disable-next=c-extension-no-member
        if init_state == tango._tango.DevState.ON:
            print("[ WARN ] device is already on")
        else:
            self.device_on()
        self.device_status()
        return 0

    def test_standby(self, dev_sim: int | None) -> int:
        """
        Test that device can be placed into standby mode.

        :param dev_sim: flag for hardware simulation.
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        if dev_sim is not None:
            self.set_simulation_mode(dev_sim)
        self.get_admin_mode()
        self.device_standby()
        self.device_status()
        return 0

    def test_status(self) -> int:
        """
        Test that device status can be read.

        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        self.get_admin_mode()
        self.device_status()
        return 0

    def test_simulation_mode(self, dev_sim: int | None) -> int:
        """
        Test that device hardware simulation can be set.

        :param dev_sim: flag for hardware simulation.
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        self.set_simulation_mode(dev_sim)
        self.get_simulation_mode()
        return 0

    def test_all(self, show_attrib: bool) -> int:
        """
        Test everything that device can do.

        :param show_attrib: flag for attributes display.
        :return: error condition
        """
        self.check_device()
        self.get_simulation_mode()
        self.show_device_attributes()
        self.show_device_commands()
        # Read admin mode, turn on ond off
        init_admin_mode = self.get_admin_mode()
        if self.adminMode is not None:
            self.admin_mode_on()
            self.admin_mode_off()
        # Read state
        init_state = self.device_status()
        # Turn device on
        # pylint: disable-next=c-extension-no-member
        if init_state == tango._tango.DevState.ON:
            print("[ WARN ] device is already on")
        else:
            self.device_on()
        self.device_status()
        # Read attribute values
        if show_attrib:
            self.read_device_attributes()
        else:
            print("[ WARN ] skip reading attributes")
        # Turn device off
        self.device_off()
        self.device_status()
        # pylint: disable-next=c-extension-no-member
        if self.dev_state == tango._tango.DevState.ON:
            print("[FAILED] device is still on")
        # Turn device back on, if neccesary
        # pylint: disable-next=c-extension-no-member
        if init_state == tango._tango.DevState.ON:
            print("[ WARN ] turn device back on")
            self.device_on()
            self.device_status()
        # Turn device admin mode back on, if neccesary
        if init_admin_mode == 1:
            print("[ WARN ] turn admin mode back to on")
            self.admin_mode_on()
        return 0

    def test_subscribe(self, attrib: str) -> int:
        """
        Test subscribed to event.

        :param attrib: attribute name
        :return: error condition
        """
        print(f"[  OK  ] subscribe to events for {self.dev_name} {attrib}")
        evnt_id: Any = self.dev.subscribe_event(
            attrib, tango.EventType.CHANGE_EVENT, tango.utils.EventCallback()
        )
        print(f"[  OK  ] subscribed to event ID {evnt_id}")
        time.sleep(15)
        try:
            events = self.dev.get_events(evnt_id)
            print(f"[  OK  ] got events {events}")
        except tango.EventSystemFailed as terr:
            print(f"[ WARN ] got no events for {self.dev_name} {attrib}")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
        try:
            self.dev.devc.unsubscribe_event(evnt_id)
            print(f"[  OK  ] unsubscribed from event ID {evnt_id}")
        except AttributeError as terr:
            print(f"[ WARN ] could not unsubscribe from event ID {evnt_id}")
            self.logger.debug(terr)
        return 0


class TestTangoDevices:
    """Compile a list of available Tango devices."""

    def __init__(self, logger: logging.Logger, evrythng: bool, cfg_data: Any):
        """
        Read Tango device names.

        :param logger: logging handle
        :param evrythng: add the kitchen sink
        :param cfg_data: configuration data
        """
        self.logger = logger
        self.tango_devices: list = []
        # Connect to database
        try:
            database = tango.Database()
        except Exception:
            tango_host = os.getenv("TANGO_HOST")
            print("[FAILED] Could not connect to Tango database %s", tango_host)
        # Read devices
        device_list = database.get_device_exported("*")
        print(f"[  OK  ] {len(device_list)} devices available")

        for device in sorted(device_list.value_string):
            # Check device name against mask
            if not evrythng:
                chk_fail = False
                for dev_chk in cfg_data["ignore_device"]:
                    chk_len = len(dev_chk)
                    if device[0:chk_len] == dev_chk:
                        chk_fail = True
                        break
                if chk_fail:
                    self.logger.debug("'%s' matches '%s'", device, cfg_data["ignore_device"])
                    continue
            self.logger.debug("Add device %s", device)
            self.tango_devices.append(device)

        self.logger.info("Found %d devices", len(self.tango_devices))
