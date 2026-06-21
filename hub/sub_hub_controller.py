"""
Swarm Park Guardian — Sub-Hub Controller
Author: A. Jyotheeswar Reddy, Manipal University Jaipur, 2026

Runs on: Raspberry Pi 4 inside each sub-hub vault
Controls: Tool carousel (4 bays), battery swap robot,
          scissor lift, waste blower, landing pad roller conveyor

Patent Claims 1(b), 3, 4 — retractable underground sub-hub.
"""

import time
import logging
from enum import Enum
from typing import Dict, Optional

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False

log = logging.getLogger('SubHub')


class ToolBay(Enum):
    BAY_0 = 0   # blade
    BAY_1 = 1   # arm
    BAY_2 = 2   # net
    BAY_3 = 3   # leaf_basket


TOOL_BAY_MAP = {
    "blade":       ToolBay.BAY_0,
    "arm":         ToolBay.BAY_1,
    "net":         ToolBay.BAY_2,
    "leaf_basket": ToolBay.BAY_3,
    "none":        None,
}

# GPIO pins for sub-hub (BCM)
SUBHUB_PINS = {
    'SCISSOR_LIFT_UP':   4,    # Raise platform
    'SCISSOR_LIFT_DOWN': 5,    # Lower platform (retract underground)
    'LID_OPEN':          6,    # Open flush lid
    'LID_CLOSED_SENSOR': 13,   # Input: lid fully closed
    'LID_OPEN_SENSOR':   19,   # Input: lid fully open
    'CAROUSEL_STEP':     26,   # Step motor pulse
    'CAROUSEL_DIR':      21,   # Step motor direction
    'CAROUSEL_HOME':     20,   # Input: home sensor
    'BATTERY_EJECT':     14,   # Solenoid: eject spent battery
    'BATTERY_INSERT':    15,   # Solenoid: insert fresh battery
    'BATTERY_LOCKED':    18,   # Input: battery latched
    'ROLLER_FWD':        23,   # Roller conveyor forward (tool bay → battery bay)
    'ROLLER_REV':        24,   # Roller conveyor reverse
    'BLOWER_PWM':        12,   # 200W waste blower PWM
    'PROXIMITY_LID':     25,   # Input: obstacle above lid
}


class SubHubController:
    """
    Controls one sub-hub unit.
    Handles: emerge/retract cycle, tool carousel rotation,
    battery swap, waste blower, roller conveyor.
    """

    CAROUSEL_STEPS_PER_BAY = 200   # stepper motor steps between bays
    BATTERY_SWAP_TIMEOUT_S = 60    # max time for swap (Patent spec)
    LID_RETRY_DELAY_S      = 300   # 5 min wait if lid obstructed (Claim 5 of failsafe)
    LID_MAX_RETRIES        = 3

    def __init__(self, hub_id: int):
        self.hub_id = hub_id
        self.carousel_position = 0   # current bay index 0–3
        self.is_emerged = False
        self.waste_bin_pct = 0
        self._setup_gpio()
        log.info(f"SubHub {hub_id} initialised")

    def _setup_gpio(self):
        if not HW_AVAILABLE:
            return
        for name, pin in SUBHUB_PINS.items():
            if name.endswith('SENSOR') or name == 'PROXIMITY_LID':
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            else:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    # ------------------------------------------------------------------
    # EMERGE / RETRACT — scissor lift + lid
    # Patent Claim 3: sub-hub retracts via scissor lift, concealed by flush lid
    # ------------------------------------------------------------------
    def emerge(self) -> bool:
        """Open lid, raise platform to surface level."""
        log.info(f"SubHub {self.hub_id}: emerging")

        # Check lid obstruction (Patent failsafe: Section 5)
        for attempt in range(self.LID_MAX_RETRIES):
            if HW_AVAILABLE and GPIO.input(SUBHUB_PINS['PROXIMITY_LID']):
                log.warning(f"SubHub {self.hub_id}: lid obstruction detected — waiting {self.LID_RETRY_DELAY_S}s")
                time.sleep(self.LID_RETRY_DELAY_S)
            else:
                break
        else:
            log.error(f"SubHub {self.hub_id}: lid blocked after {self.LID_MAX_RETRIES} retries — alerting supervisor")
            self._alert_supervisor("lid_blocked")
            return False

        if HW_AVAILABLE:
            GPIO.output(SUBHUB_PINS['LID_OPEN'], GPIO.HIGH)
            # Wait for lid fully open
            timeout = time.time() + 10
            while not GPIO.input(SUBHUB_PINS['LID_OPEN_SENSOR']):
                if time.time() > timeout:
                    log.error(f"SubHub {self.hub_id}: lid open timeout")
                    return False
                time.sleep(0.1)
            GPIO.output(SUBHUB_PINS['LID_OPEN'], GPIO.LOW)

            # Raise scissor lift
            GPIO.output(SUBHUB_PINS['SCISSOR_LIFT_UP'], GPIO.HIGH)
            time.sleep(4)   # ~4 seconds for full extension
            GPIO.output(SUBHUB_PINS['SCISSOR_LIFT_UP'], GPIO.LOW)
        else:
            time.sleep(0.1)  # simulation

        self.is_emerged = True
        log.info(f"SubHub {self.hub_id}: emerged and ready")
        return True

    def retract(self) -> bool:
        """Lower platform, close flush lid — invisible during daytime."""
        log.info(f"SubHub {self.hub_id}: retracting underground")
        if HW_AVAILABLE:
            GPIO.output(SUBHUB_PINS['SCISSOR_LIFT_DOWN'], GPIO.HIGH)
            time.sleep(4)
            GPIO.output(SUBHUB_PINS['SCISSOR_LIFT_DOWN'], GPIO.LOW)
            # Close lid
            GPIO.output(SUBHUB_PINS['LID_OPEN'], GPIO.LOW)
            timeout = time.time() + 10
            while not GPIO.input(SUBHUB_PINS['LID_CLOSED_SENSOR']):
                if time.time() > timeout:
                    log.error(f"SubHub {self.hub_id}: lid close timeout")
                    return False
                time.sleep(0.1)
        else:
            time.sleep(0.1)
        self.is_emerged = False
        log.info(f"SubHub {self.hub_id}: retracted and hidden")
        return True

    # ------------------------------------------------------------------
    # TOOL CAROUSEL — 4-bay rotation
    # Patent Claim 1(b): tool carousel stores 4 interchangeable modules
    # ------------------------------------------------------------------
    def rotate_carousel_to(self, tool_name: str) -> bool:
        target_bay = TOOL_BAY_MAP.get(tool_name)
        if target_bay is None:
            log.info(f"No tool swap needed for: {tool_name}")
            return True

        steps_needed = (target_bay.value - self.carousel_position) % 4
        log.info(f"SubHub {self.hub_id}: rotating carousel {steps_needed} bays to {tool_name}")

        if HW_AVAILABLE:
            dir_pin = SUBHUB_PINS['CAROUSEL_DIR']
            step_pin = SUBHUB_PINS['CAROUSEL_STEP']
            GPIO.output(dir_pin, GPIO.HIGH)
            for _ in range(steps_needed * self.CAROUSEL_STEPS_PER_BAY):
                GPIO.output(step_pin, GPIO.HIGH)
                time.sleep(0.002)
                GPIO.output(step_pin, GPIO.LOW)
                time.sleep(0.002)
        else:
            time.sleep(0.05 * steps_needed)

        self.carousel_position = target_bay.value
        log.info(f"SubHub {self.hub_id}: carousel at {tool_name}")
        return True

    # ------------------------------------------------------------------
    # BATTERY SWAP — under 60 seconds (Patent spec Section 12)
    # Patent Claim 4: dual-bay landing pad with roller conveyor
    # ------------------------------------------------------------------
    def battery_swap(self, drone_id: int) -> bool:
        """Full battery swap sequence: eject spent → insert fresh."""
        log.info(f"SubHub {self.hub_id}: battery swap for Drone {drone_id}")
        start = time.time()

        if HW_AVAILABLE:
            # Move drone on roller from tool bay to battery bay
            GPIO.output(SUBHUB_PINS['ROLLER_FWD'], GPIO.HIGH)
            time.sleep(2)
            GPIO.output(SUBHUB_PINS['ROLLER_FWD'], GPIO.LOW)

            # Eject spent battery
            GPIO.output(SUBHUB_PINS['BATTERY_EJECT'], GPIO.HIGH)
            time.sleep(1)
            GPIO.output(SUBHUB_PINS['BATTERY_EJECT'], GPIO.LOW)
            time.sleep(0.5)

            # Insert fresh battery
            GPIO.output(SUBHUB_PINS['BATTERY_INSERT'], GPIO.HIGH)
            time.sleep(1)
            GPIO.output(SUBHUB_PINS['BATTERY_INSERT'], GPIO.LOW)

            # Verify battery locked
            timeout = time.time() + 10
            while not GPIO.input(SUBHUB_PINS['BATTERY_LOCKED']):
                if time.time() > timeout:
                    log.error(f"SubHub {self.hub_id}: battery latch failed — re-inserting old battery")
                    # Patent failsafe: re-insert old battery and signal error
                    GPIO.output(SUBHUB_PINS['BATTERY_INSERT'], GPIO.HIGH)
                    time.sleep(1)
                    GPIO.output(SUBHUB_PINS['BATTERY_INSERT'], GPIO.LOW)
                    self._alert_supervisor(f"battery_swap_failed_drone_{drone_id}")
                    return False
                time.sleep(0.1)

            # Move drone back to tool bay
            GPIO.output(SUBHUB_PINS['ROLLER_REV'], GPIO.HIGH)
            time.sleep(2)
            GPIO.output(SUBHUB_PINS['ROLLER_REV'], GPIO.LOW)
        else:
            time.sleep(0.1)  # simulation

        elapsed = time.time() - start
        log.info(f"SubHub {self.hub_id}: battery swap complete in {elapsed:.1f}s (limit: {self.BATTERY_SWAP_TIMEOUT_S}s)")
        return True

    # ------------------------------------------------------------------
    # WASTE BLOWER — 200W regenerative (Patent Claim 8)
    # ------------------------------------------------------------------
    def start_waste_blower(self, power_pct: int = 100):
        log.info(f"SubHub {self.hub_id}: waste blower ON at {power_pct}%")
        if HW_AVAILABLE:
            pwm = GPIO.PWM(SUBHUB_PINS['BLOWER_PWM'], 400)
            pwm.start(power_pct)
        self._blower_pwm = getattr(self, '_blower_pwm', None)

    def stop_waste_blower(self):
        log.info(f"SubHub {self.hub_id}: waste blower OFF")
        if HW_AVAILABLE and hasattr(self, '_blower_pwm') and self._blower_pwm:
            self._blower_pwm.stop()

    # ------------------------------------------------------------------
    # SUPERVISOR ALERT
    # ------------------------------------------------------------------
    def _alert_supervisor(self, code: str):
        log.critical(f"SubHub {self.hub_id}: SUPERVISOR ALERT — {code}")
        # In production: send MQTT message to main hub supervisor dashboard

    def cleanup(self):
        if HW_AVAILABLE:
            GPIO.cleanup()
