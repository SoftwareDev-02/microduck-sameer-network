"""Run a deterministic, synthetic skill-sharing walkthrough."""
from network import Agent, Evaluation, SkillPackage, SkillRegistry, request_human_promotion


def main() -> None:
    registry = SkillRegistry()
    teacher = Agent("duck-01", "balance")
    learner = Agent("duck-02", "recovery")
    package = SkillPackage(
        skill_id="balance-recovery",
        version=1,
        task="recover balance after a small simulated perturbation",
        source_agent=teacher.agent_id,
        policy_reference="demo://synthetic-policy-not-executable",
        evaluation=Evaluation(trials=50, success_rate=0.90, regression_rate=0.02),
    )
    registry.publish(package)
    learner.local_evaluations[package.skill_id] = Evaluation(
        trials=30, success_rate=0.87, regression_rate=0.03
    )
    accepted = learner.review_shared_skill(registry.get(package.skill_id, 1))
    print(f"Published packages: {len(registry.list_packages())}")
    print(f"Receiver replay: {'PASS' if accepted else 'FAIL'}")
    print(f"Package state: {package.state.value}")
    promoted = request_human_promotion(package, human_approved=False)
    print(f"Human promotion approved: {promoted}")
    print("Hardware action: NOT AVAILABLE in this prototype")


if __name__ == "__main__":
    main()
