# Hardware Setup Guide
**Swarm Park Guardian — A. Jyotheeswar Reddy, Manipal University Jaipur, 2026**

---

## Drone Assembly (per unit, target <2 kg)

| Component | Part | Supplier | Approx. Cost (INR) |
|---|---|---|---|
| Frame | Carbon fibre quad, 45cm M2M | Custom / AliExpress | ₹3,500 |
| Motors (4×) | T-Motor F40 Pro IV 2400KV | RCDhamaka | ₹6,000 |
| Propellers (4×) | 9×5 inch carbon fibre | RCDhamaka | ₹800 |
| Flight Controller | Pixhawk 6C Mini | Holybro | ₹12,000 |
| Battery | Tattu 5000mAh 6S 45C LiPo | GetFPV | ₹8,500 |
| Supercapacitor | 50F 16V Maxwell BCAP0050 | Mouser | ₹1,200 |
| AI Vision | OAK-D Pro W | Luxonis | ₹35,000 |
| AI Processor | Raspberry Pi 4 4GB | RPi Foundation | ₹5,500 |
| Edge TPU | Google Coral USB Accelerator | Google | ₹4,500 |
| Thermal camera | FLIR Lepton 3.5 + breakout | GroupGets | ₹18,000 |
| Radio | mRo SiK Telemetry 433MHz | mRo | ₹3,500 |
| Universal Bay | Custom dovetail + electromagnet | Custom | ₹2,500 |
| LED Ring | WS2812B 144 LED/m ring | AliExpress | ₹400 |
| Anti-collision strobe | 400cd white strobe | AliExpress | ₹600 |
| **Total per drone** | | | **~₹1,02,500** |

---

## Raspberry Pi 4 Setup (Onboard Drone)

```bash
# 1. Flash Raspberry Pi OS Lite (64-bit)
# 2. Enable SSH, I2C, SPI, UART in raspi-config

# 3. Install dependencies
pip install -r requirements_hardware.txt

# 4. Install MAVSDK server
wget https://github.com/mavlink/MAVSDK/releases/download/v1.4.17/mavsdk_server_linux-arm64
chmod +x mavsdk_server_linux-arm64
sudo mv mavsdk_server_linux-arm64 /usr/local/bin/mavsdk_server

# 5. Install Coral Edge TPU runtime
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt-get update && sudo apt-get install libedgetpu1-std

# 6. Connect Pixhawk 6C via UART (/dev/ttyAMA0, 57600 baud)
# 7. Test connection
python -c "import asyncio; from mavsdk import System; drone=System(); asyncio.run(drone.connect('serial:///dev/ttyAMA0:57600'))"
```

---

## PX4 Configuration (Pixhawk 6C)

1. Flash PX4 v1.14+ via QGroundControl
2. Enable offboard mode: `COM_RCL_EXCEPT = 4`
3. Set failsafe: `NAV_RCL_ACT = 3` (Return to Launch on RC loss)
4. Enable night strobe: configure AUX output for LED
5. Set geofence to park boundary polygon

---

## Sub-Hub Wiring (Raspberry Pi 4 → GPIO)

See `hub/sub_hub_controller.py` for full GPIO pin map.

```
Pin 17 (BCM) → Scissor Lift UP relay
Pin 18 (BCM) → 200W Blower PWM
Pin 23 (BCM) → Stepper STEP (carousel)
Pin 24 (BCM) → Stepper DIR (carousel)
Pin 14 (BCM) → Battery Eject solenoid
Pin 15 (BCM) → Battery Insert solenoid
```

---

## DGCA Night Flying Compliance

- Drone weight: **1,985g** (under 2kg micro category)
- Anti-collision light: **400cd white strobe, 40 flashes/min** (onboard)
- Night ops window: **1:00 AM – 7:00 AM** (submit DGCA advance notice)
- Geofence: Park boundary hardcoded in PX4 parameters
- Remote pilot certificate: required for test flights
