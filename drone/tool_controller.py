"""
Swarm Park Guardian — Universal Tool Bay Controller
Author: A. Jyotheeswar Reddy, Manipal University Jaipur, 2026

Controls the dovetail + electromagnet + pogo-pin universal receiver bay.
Manages 4 tool modules: blade, arm, net, leaf basket.
Runs on: Raspberry Pi 4 GPIO onboard the drone.

Patent Claims 1(c), 2, 4 — interchangeable task-specific tool modules.
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False
    print("[ToolController] RPi.GPIO not found — running in simulation mode")

log = logging.getLogger('ToolController')


class ToolModule(Enum):
    NONE        = "none"
    BLADE       = "blade"        # 150mm rotary cutter, brushless, servo-retractable
    ARM         = "arm"          # 2-DOF servo gripper, 200g payload, 15cm reach
    NET         = "net"          # 30cm nano-mesh net, servo-deployed downward
    LEAF_BASKET = "leaf_basket"  # 2L collection basket, servo-hinged lid


# GPIO pin assignments (BCM numbering, Raspberry Pi 4)
PINS = {
    'ELECTROMAGNET':    17,   # HIGH = energised (tool locked), LOW = release
    'DOVETAIL_LOCK':    27,   # Servo PWM — dovetail locking pin
    'POGO_VERIFY':      22,   # Input — HIGH when pogo pins seated correctly
    'BLADE_PWM':        18,   # Brushless ESC signal for cutter disc
    'BLADE_RETRACT':    23,   # Servo — retract/deploy blade guard
    'ARM_SERVO_YAW':    24,   # Servo PWM — arm base rotation
    'ARM_SERVO_GRIP':   25,   # Servo PWM — gripper open/close
    'NET_DEPLOY':       8,    # Servo — net deploy/retract
    'BASKET_LID':       7,    # Servo — basket lid open/close
    'DUST_BLASTER':     12,   # PWM — 40W brushless nozzle speed
    'IRRIGATION_VALVE': 16,   # Solenoid — irrigation coupling open/close
}


class ToolController:
    """
    Controls tool bay electromagnet, dovetail lock, and all 4 modules.
    Verifies pogo-pin electrical connection before activating any tool.
    """

    def __init__(self):
        self.current_tool: ToolModule = ToolModule.NONE
        self._setup_gpio()

    def _setup_gpio(self):
        if not HW_AVAILABLE:
            return
        for name, pin in PINS.items():
            if name in ('POGO_VERIFY',):
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            else:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        log.info("GPIO pins configured")

    # ------------------------------------------------------------------
    # TOOL LOCK / UNLOCK  (called at sub-hub during swap)
    # ------------------------------------------------------------------
    def lock_tool(self, tool: ToolModule) -> bool:
        """Energise electromagnet and verify pogo-pin connection."""
        log.info(f"Locking tool: {tool.value}")
        if HW_AVAILABLE:
            GPIO.output(PINS['ELECTROMAGNET'], GPIO.HIGH)
            time.sleep(0.3)
            # Verify pogo pins seated
            if not GPIO.input(PINS['POGO_VERIFY']):
                log.error("Pogo pins NOT seated — tool lock failed")
                GPIO.output(PINS['ELECTROMAGNET'], GPIO.LOW)
                return False
        self.current_tool = tool
        log.info(f"Tool {tool.value} locked and verified")
        return True

    def unlock_tool(self) -> bool:
        """De-energise electromagnet to release tool at sub-hub."""
        log.info(f"Releasing tool: {self.current_tool.value}")
        if HW_AVAILABLE:
            GPIO.output(PINS['ELECTROMAGNET'], GPIO.LOW)
            time.sleep(0.2)
        self.current_tool = ToolModule.NONE
        return True

    # ------------------------------------------------------------------
    # BLADE MODULE — Patent Claim 2, 150mm rotary cutter
    # ------------------------------------------------------------------
    def blade_deploy(self):
        """Deploy blade guard and spin up cutter to working RPM."""
        assert self.current_tool == ToolModule.BLADE, "Blade module not attached"
        log.info("Blade: deploying guard, spinning up")
        if HW_AVAILABLE:
            GPIO.output(PINS['BLADE_RETRACT'], GPIO.HIGH)   # lower guard
            time.sleep(0.5)
            # PWM at 50% duty = working speed
            pwm = GPIO.PWM(PINS['BLADE_PWM'], 400)
            pwm.start(50)
        log.info("Blade: ready — cutting at 5cm hover")

    def blade_retract(self):
        log.info("Blade: stopping and retracting")
        if HW_AVAILABLE:
            GPIO.output(PINS['BLADE_PWM'], GPIO.LOW)
            time.sleep(0.3)
            GPIO.output(PINS['BLADE_RETRACT'], GPIO.LOW)

    # ------------------------------------------------------------------
    # ARM MODULE — 2-DOF servo gripper
    # ------------------------------------------------------------------
    def arm_open(self):
        assert self.current_tool == ToolModule.ARM
        log.info("Arm: opening gripper")
        if HW_AVAILABLE:
            GPIO.output(PINS['ARM_SERVO_GRIP'], GPIO.LOW)

    def arm_close(self):
        assert self.current_tool == ToolModule.ARM
        log.info("Arm: closing gripper")
        if HW_AVAILABLE:
            GPIO.output(PINS['ARM_SERVO_GRIP'], GPIO.HIGH)

    def arm_rotate(self, angle_deg: int):
        """Rotate arm base 0–180 degrees."""
        assert self.current_tool == ToolModule.ARM
        log.info(f"Arm: rotating to {angle_deg}°")
        # Servo pulse width: 1ms (0°) to 2ms (180°)
        if HW_AVAILABLE:
            pwm = GPIO.PWM(PINS['ARM_SERVO_YAW'], 50)
            duty = 2.5 + (angle_deg / 180.0) * 10.0
            pwm.start(duty)
            time.sleep(0.5)
            pwm.stop()

    # ------------------------------------------------------------------
    # NET MODULE — 30cm nano-mesh net
    # ------------------------------------------------------------------
    def net_deploy(self):
        assert self.current_tool == ToolModule.NET
        log.info("Net: deploying downward")
        if HW_AVAILABLE:
            GPIO.output(PINS['NET_DEPLOY'], GPIO.HIGH)
        time.sleep(0.8)

    def net_retract(self):
        assert self.current_tool == ToolModule.NET
        log.info("Net: retracting")
        if HW_AVAILABLE:
            GPIO.output(PINS['NET_DEPLOY'], GPIO.LOW)
        time.sleep(0.8)

    # ------------------------------------------------------------------
    # LEAF BASKET MODULE — 2L, servo-hinged lid
    # ------------------------------------------------------------------
    def basket_open(self):
        assert self.current_tool == ToolModule.LEAF_BASKET
        log.info("Basket: opening lid")
        if HW_AVAILABLE:
            GPIO.output(PINS['BASKET_LID'], GPIO.HIGH)

    def basket_close(self):
        assert self.current_tool == ToolModule.LEAF_BASKET
        log.info("Basket: closing lid")
        if HW_AVAILABLE:
            GPIO.output(PINS['BASKET_LID'], GPIO.LOW)

    # ------------------------------------------------------------------
    # PERMANENT ONBOARD TOOLS (no module swap needed)
    # ------------------------------------------------------------------
    def dust_blast(self, power_pct: int = 80, duration_s: float = 3.0):
        """Fire 40W brushless dust blaster nozzle (permanent, no module)."""
        log.info(f"Dust blaster: {power_pct}% for {duration_s}s")
        if HW_AVAILABLE:
            pwm = GPIO.PWM(PINS['DUST_BLASTER'], 400)
            pwm.start(power_pct)
            time.sleep(duration_s)
            pwm.stop()
        else:
            time.sleep(duration_s)

    def irrigation_open(self):
        """Open retractable irrigation coupling solenoid."""
        log.info("Irrigation: coupling open — water flowing from ground socket")
        if HW_AVAILABLE:
            GPIO.output(PINS['IRRIGATION_VALVE'], GPIO.HIGH)

    def irrigation_close(self):
        log.info("Irrigation: coupling closed")
        if HW_AVAILABLE:
            GPIO.output(PINS['IRRIGATION_VALVE'], GPIO.LOW)

    def cleanup(self):
        if HW_AVAILABLE:
            GPIO.cleanup()
