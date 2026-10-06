# Drone Autonomy

A quadrotor that maps unknown rooms with a depth camera, plans with A*, and adapts to payload, wind and motor wear, using seven meta-learning algorithms combined with classical control and planning. Everything runs in simulation, with a plan for real flights on a Holybro X500 V2.

![Two recorded flights: the map built from depth, the final A* plan and the flown track](docs/images/flights.png)

![The same figure-eight with extra payload, wind and a worn motor: fixed gains vs L1 adaptive control](docs/images/tracking.png)

**[Live demo: replay the recorded flights](https://amalmehta.github.io/DroneAutonomy/)**

| | |
|---|---|
| [Setup, run and use](docs/INSTRUCTIONS.md) | install, train, benchmark, record the demo |
| [System design](docs/SYSTEM-DESIGN.md) | architecture, components, flows, decisions, limits |
| [File structure](docs/FILE-STRUCTURE.md) | what's where |
| [Drone selection](docs/DRONE-SELECTION.md) | which drone to fly the stack on, and the test plan |

Status: the simulator, the full navigation stack, all seven meta-learning algorithms and the baselines are built. Training runs are in progress; results, the paper and the results section of the website will follow.
