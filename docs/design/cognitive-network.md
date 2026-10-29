# Cognitive network architecture proposal

## Goal
Explore whether multiple Microduck instances can improve task performance by sharing reviewed, versioned skills while preserving the existing robot runtime's safety and reliability.

## Separation of concerns

- **Robot runtime (existing):** deterministic control loop, sensors, actuators, communications and signed update path. Do not insert experimental learning into the real-time loop.
- **Training/evaluation (existing adjacent project):** MuJoCo/PPO policy training, domain randomization, evaluation and ONNX export.
- **Network experiment (new isolated scaffold):** agent identities, skill-package metadata, provenance, receiver-side replay results and promotion gates.
- **Cognitive Lab UI (Figma concept):** observes network state and experiment evidence; current metrics are illustrative only.

## Skill exchange lifecycle

`observe → train in simulation → package with provenance → share → receiver replay → compare regressions → human review → supervised bench validation`

A package must identify task, version, source agent, policy artifact, environment, trial count, success rate and regression rate. Receiving agents must run their own evaluation; a teacher's score alone is not enough. Conflicting or weak skills remain rejected rather than being silently propagated.

## Initial acceptance criteria

1. Multiple synthetic agents can share a versioned skill descriptor.
2. Duplicate skill versions and invalid metrics are rejected.
3. A receiver only verifies a skill when both source evidence and receiver replay pass thresholds.
4. Promotion requires a verified skill and explicit human approval.
5. The prototype cannot send commands to hardware or deploy policy artifacts.
6. Unit tests cover passing, missing evidence, weak evidence, duplicate packages, and the approval gate.

## Non-goals for the first prototype

- No claims of consciousness, general intelligence, or a learned model of all reality.
- No live motor control, automatic policy installation, or unattended hardware experimentation.
- No claim that synthetic demo metrics represent a physical robot.

## Later experiments

- Define tasks and observation/action schemas compatible with the current MuJoCo model.
- Train distinct policies with controlled variations in friction, mass, sensor noise and disturbances.
- Compare independent learning, teacher-student transfer, and shared replay buffers with fixed seeds.
- Track confidence, regression rates, environment compatibility and policy lineage.
- Require rollback artifacts, signed packages, supervised bench testing and an emergency stop before any physical trial.
