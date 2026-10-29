# Microduck Cognitive Network — simulation-first prototype

This isolated experiment explores the Microduck network idea without changing the robot's real-time Rust daemons. It models several duck agents, skill packages, evidence-based review, and a guarded promotion path. It is a research scaffold, not a trained cognitive system and not connected to hardware.

## Safety boundary

- The prototype is simulation-only and has no motor, Bluetooth, network, or robot-control adapter.
- Agent metrics and example skills are synthetic fixtures, not telemetry from a physical duck.
- Skill sharing moves metadata and evidence summaries, not executable policies.
- Hardware promotion is deliberately a policy decision requiring simulation evidence and human approval. This prototype does not implement deployment.

## Run

Requires Python 3.10+ and only the standard library.

```bash
python -m unittest discover -s experiments/microduck-network/tests -v
python experiments/microduck-network/demo.py
```

## Concept loop

1. **Observe** — record a bounded task result and context.
2. **Learn** — create a candidate skill with provenance and measurable evidence.
3. **Teach** — publish a versioned package to the shared skill registry.
4. **Verify** — a receiving agent replays it against its own evidence requirements.
5. **Promote** — require minimum evidence and explicit human approval; otherwise keep simulation-only.

## Package contract

Each skill has a stable ID, version, source agent, task, policy reference, evaluation metrics, environment metadata, and approval state. The registry rejects duplicate versions and malformed evidence. This first cut is intentionally small so it can later be adapted to the repository's existing MuJoCo/PPO training workflow without coupling the core robot services to an experimental learning loop.

## Next integration steps

- Connect the skill registry to the existing `microduck_rl` training/evaluation pipeline.
- Add domain-randomized MuJoCo trials and reproducible run artifacts.
- Define a signed, portable policy artifact format and compatibility checks.
- Add a human-reviewed bridge to existing policy update mechanisms only after regression, rollback, and supervised bench tests exist.
