import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from network import Agent, Evaluation, SkillPackage, SkillRegistry, SkillState, request_human_promotion  # noqa: E402


def package() -> SkillPackage:
    return SkillPackage(
        skill_id="balance", version=1, task="recover", source_agent="duck-a",
        policy_reference="artifact://policy-v1",
        evaluation=Evaluation(30, 0.90, 0.02),
    )


class NetworkTests(unittest.TestCase):
    def test_publish_and_receiver_replay(self):
        registry = SkillRegistry()
        p = package()
        registry.publish(p)
        learner = Agent("duck-b", "recovery", {"balance": Evaluation(25, 0.85, 0.03)})
        self.assertTrue(learner.review_shared_skill(registry.get("balance", 1)))
        self.assertEqual(p.state, SkillState.VERIFIED)

    def test_duplicate_version_rejected(self):
        registry = SkillRegistry()
        registry.publish(package())
        with self.assertRaises(ValueError):
            registry.publish(package())

    def test_missing_receiver_evidence_rejects(self):
        p = package()
        self.assertFalse(Agent("duck-b", "recovery").review_shared_skill(p))
        self.assertEqual(p.state, SkillState.REJECTED)

    def test_weak_source_evidence_rejects(self):
        p = package()
        p.evaluation = Evaluation(4, 0.50, 0.25)
        self.assertFalse(Agent("duck-b", "recovery", {"balance": Evaluation(30, 0.90, 0.01)}).review_shared_skill(p))

    def test_human_gate_never_deploys(self):
        p = package()
        p.state = SkillState.VERIFIED
        self.assertFalse(request_human_promotion(p, human_approved=False))
        self.assertEqual(p.state, SkillState.VERIFIED)
        self.assertTrue(request_human_promotion(p, human_approved=True))
        self.assertEqual(p.state, SkillState.APPROVED_FOR_REVIEW)

    def test_bad_metrics_rejected(self):
        p = package()
        p.evaluation = Evaluation(10, 1.5, 0.0)
        with self.assertRaises(ValueError):
            p.validate()


if __name__ == "__main__":
    unittest.main()
