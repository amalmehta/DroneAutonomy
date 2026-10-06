# Drone Selection: which drone runs the stack in the real world

**Pick: Holybro X500 V2 PX4 Development Kit + NVIDIA Jetson Orin Nano Super + Intel RealSense D435i (≈ $1.6–2.0k).**
Runner-up: Bitcraze Crazyflie 2.1 Brushless (policy-transfer checks only). Conditional pick: ModalAI Starling 2, if you can get one.

Research date: 2026-10-05. Prices are from manufacturer stores on that date and change. **est.** = our estimate, not a published value.

## Requirements the stack puts on the drone

| Stack piece | What it needs from the hardware |
|---|---|
| RL / meta-RL policies (residual, local planner) | Flight controller that accepts **collective thrust + body rates** (or velocity) from a companion computer at ≥ 50 Hz |
| Perception + mapping | A **depth camera** (the sim models a D435i: 87°×58° FOV, 0.3–3 m best range) and enough compute for a 3D occupancy map |
| Global planner | Companion CPU for A* on a voxel grid |
| Adaptation (meta-learning) | Logged flight data on board, compute to take a few gradient steps or run a context encoder |
| Indoor testing | Safe in a netted cage; motion capture or VIO for state |

## Comparison

| | **X500 V2 + Jetson + D435i** | **Crazyflie 2.1 Brushless** | **Starling 2 (D0014)** | **Starling 2 Max** | **PX4 Vision V1.5** | **Agilicious** |
|---|---|---|---|---|---|---|
| Price (USD) | Kit $609–769, Jetson $249 MSRP ($399 street), D435i $399, extras ≈ $300 → **≈ $1.6–2.0k (est.)** | ≈ $0.5–1k with decks | $2,949.99 last listed; **appears unavailable new** | $4,199.99–6,799.99 | $1,889.99, **sold out** | BOM only, build yourself |
| Takeoff mass | ≈ 1.9–2.1 kg (est.) | 34–37 g | 285 g | 566 g | 893 g (no battery) | 750 g |
| Size | 500 mm wheelbase, 10" props | 100 mm diagonal | 230 mm diagonal | 512 mm | 286 mm | 5" props |
| Flight time | ≈ 10–14 min with payload (est.) | ≈ 10 min | > 35 min | ≈ 40–55 min | not found | not found |
| Compute | Orin Nano Super, up to 67 TOPS, 8 GB | STM32F405 (+ GAP8 on AI deck) | VOXL 2, 15 TOPS | VOXL 2 | Atom x5-z8350 | Jetson TX2 (EOL) |
| Depth sensing | **D435i active stereo**, 87°×58°, 0.3–3 m | none (5 single-zone ToF rangers) | PMD ToF 240×180, 0.1–6 m | ToF only on C29 config | Structure Core (discontinued) | RealSense in paper |
| State estimation | Integrate VIO yourself (Isaac ROS VSLAM / OpenVINS) or mocap | Flow / Lighthouse / mocap | onboard VIO | onboard VIO | VIO / flow | VIO / mocap |
| Flight stack | PX4 (Pixhawk 6C) | Bitcraze firmware | PX4 | PX4 | PX4 | Agilicious |
| Thrust + body-rate offboard | **Yes** — `VehicleRatesSetpoint` via uXRCE-DDS, or MAVLink `SET_ATTITUDE_TARGET` | partial — documented API takes roll/pitch *angles* | yes | yes | yes | yes (native) |
| ROS 2 | yes | yes (Crazyswarm2) | yes | yes | ROS 1 era | mostly ROS 1 |
| Indoor suitability | medium — needs a netted cage | excellent | excellent | medium | medium | low (T/W ≈ 5) |

**Excluded.** DJI: closed flight controller, SDKs expose only high-level virtual-stick input, and new models are hit by the FCC Covered List (2025-12-22). Skydio: left the consumer market (2023), no low-level control API.

**US procurement note.** The FCC added foreign-made drones and critical components to its Covered List on 2025-12-22. Previously authorized models can still be sold; check each part before buying.

## Why the X500 V2 build

1. **Same command interface as the policies.** PX4 offboard `VehicleRatesSetpoint` takes body rates + collective thrust — exactly the simulator's CTBR action — over uXRCE-DDS at 50 Hz (proof-of-life above ≈ 2 Hz, `COM_OF_LOSS_T`).
2. **Same sensor as the simulator.** The sim's depth camera is modelled on the D435i, and the Jetson has headroom for mapping (nvblox / OctoMap), A*, policy inference and on-board adaptation steps.
3. **Reference airframe.** The X500 is PX4's reference airframe with an official Gazebo model, so the simulator's physical parameters (below) come from a published model rather than guesses.
4. **Payload headroom** of ≈ 1–1.5 kg covers the Jetson + camera (≈ 0.3 kg est.), which also makes the payload-adaptation experiments physically testable (add known masses).
5. **In stock.** Every other candidate is sold out, discontinued or over budget.

**Downsides.** ≈ 2 kg with 10" props indoors: fly only in a netted cage. VIO is integration work, not turnkey.

## Simulator parameters (used in `drone_autonomy/config.py`)

| Parameter | Value | Status |
|---|---|---|
| Mass | 2.0 kg | PX4 x500 model; weigh the real build |
| Arm length | 0.25 m | from 500 mm wheelbase |
| Inertia (Ixx, Iyy, Izz) | 0.0217, 0.0217, 0.040 kg·m² | PX4 sim model, not measured hardware |
| Thrust-to-weight | 2.1 | **est.** from Holybro's payload spec (sim model gives ≈ 1.7) |
| Yaw moment coefficient | 0.016 m | PX4 sim model |
| Motor time constant | 40 ms | **est.** (sim model: 12.5 ms up / 25 ms down) |
| Linear body drag | 0.3 N·s/m | **est.** |

Meta-learning tasks randomize mass (×0.85–1.3), motor efficiency, drag, wind and latency around these values, so the exact numbers matter less than their ranges — but **Stage 0 below replaces the estimates with measurements.**

## Sim-to-real test plan

**Setup.** Netted cage ≥ 6×6×3 m; Vicon/OptiTrack streamed to PX4 via `/fmu/in/vehicle_visual_odometry` for early stages, then onboard VIO with mocap kept for ground truth; ULog + ROS 2 bags.

**Safety.** RC kill switch (`RC_MAP_KILL_SW`) and offboard-exit switch, practised before any policy flight; PX4 geofence (`GF_*`) inside the cage plus a software envelope clamping rates/thrust and falling back to Hold; offboard-loss failsafe (`COM_OBL_RC_ACT`); latency watchdog (Hold if commands are > 2 cycles late); battery failsafe; tethered first flights; props-off bench test of the full pipeline; always a spotter.

| Stage | What runs | Pass criterion |
|---|---|---|
| 0. System ID | Weigh, pendulum inertia, thrust-stand curves + motor step, hover log | Update `config.py`; re-run the benchmark |
| 1. Hover | Classical controller, then residual policy, mocap state | ±10 cm for 60 s (est. target) |
| 2. Tracking | Reference trajectories, no obstacles; add known payloads for adaptation tests | RMSE within 1.5× the simulator's for the same task |
| 3. Known obstacles | Foam boxes/poles, live D435i mapping, A* + local policy, mocap state | success rate, min clearance, safety-layer interventions |
| 4. Unknown room | Same, onboard VIO only | success over N trials, time to goal, collisions, VIO drift |

## Runner-up and conditional pick

- **Crazyflie 2.1 Brushless** (37 g, guards included, Crazyswarm2): the safest way to check that control policies transfer, but it **cannot carry a depth camera** (perception would be "virtual", from mocap), and external body-rate commands likely need firmware work.
- **ModalAI Starling 2**: the best technical fit (285 g, ToF depth, on-board VIO, PX4, ROS 2) if one can be obtained used or through ModalAI sales; it can also be assembled from parts for ≈ $2.6–2.9k (est.).

## Sources

1. Holybro X500 V2 kit — https://holybro.com/products/px4-development-kit-x500-v2 · https://docs.holybro.com/drone-development-kit/px4-development-kit-x500v2
2. NVIDIA Jetson — https://developer.nvidia.com/buy-jetson · https://www.sparkfun.com/nvidia-jetson-orin-nano-developer-kit.html
3. RealSense D435i — https://store.realsenseai.com/buy-intel-realsense-depth-camera-d435i.html
4. Crazyflie 2.1 Brushless — https://www.bitcraze.io/products/crazyflie-2-1-brushless/ · setpoint API https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/functional-areas/sensor-to-control/commanders_setpoints/ · https://github.com/bitcraze/crazyflie-firmware/issues/572
5. ModalAI Starling 2 / 2 Max — https://www.modalai.com/pages/starlings · https://docs.modalai.com/starling-2-datasheet/ · https://www.modalai.com/products/starling-2-max · https://docs.modalai.com/voxl2-feature-matrix/
6. PX4 Vision V1.5 — https://holybro.com/products/px4-vision-dev-kit-v1-5
7. Agilicious — https://rpg.ifi.uzh.ch/docs/ScienceRobotics22_Foehn.pdf
8. PX4 offboard mode — https://docs.px4.io/main/en/flight_modes/offboard.html
9. PX4 x500 Gazebo model — https://github.com/PX4/PX4-gazebo-models (`models/x500_base/model.sdf`)
10. FCC Covered List — https://dronelife.com/2025/12/22/fcc-adds-foreign-made-drones-and-components-to-covered-list-citing-national-security-risks/
11. Skydio consumer exit — https://dronedj.com/2023/08/10/skydio-consumer-drone-business-shutdown/
