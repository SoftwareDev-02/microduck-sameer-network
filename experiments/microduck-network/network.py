"""Simulation-only multi-agent skill exchange scaffold. No hardware interfaces."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SkillState(str, Enum):
    CANDIDATE = "candidate"
    SHARED = "shared"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPROVED_FOR_REVIEW = "approved_for_human_review"


@dataclass(frozen=True)
class Evaluation:
    trials: int
    success_rate: float
    regression_rate: float
    environment: str = "mujoco-simulation"

    def valid(self) -> bool:
        return (
            self.trials >= 0
            and 0.0 <= self.success_rate <= 1.0
            and 0.0 <= self.regression_rate <= 1.0
            and bool(self.environment.strip())
        )


@dataclass
class SkillPackage:
    skill_id: str
    version: int
    task: str
    source_agent: str
    policy_reference: str
    evaluation: Evaluation
    state: SkillState = SkillState.CANDIDATE
    reviewers: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.skill_id.strip() or not self.task.strip() or not self.source_agent.strip():
            raise ValueError("skill_id, task, and source_agent are required")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        if not self.policy_reference.strip():
            raise ValueError("policy_reference must identify a policy artifact")
        if not self.evaluation.valid():
            raise ValueError("evaluation metrics are invalid")


class SkillRegistry:
    """In-memory registry; stores descriptors only, never loads or executes policies."""

    def __init__(self) -> None:
        self._packages: Dict[tuple[str, int], SkillPackage] = {}

    def publish(self, package: SkillPackage) -> None:
        package.validate()
        key = (package.skill_id, package.version)
        if key in self._packages:
            raise ValueError(f"skill version already exists: {package.skill_id}@{package.version}")
        package.state = SkillState.SHARED
        self._packages[key] = package

    def get(self, skill_id: str, version: int) -> SkillPackage:
        try:
            return self._packages[(skill_id, version)]
        except KeyError as exc:
            raise KeyError(f"unknown skill {skill_id}@{version}") from exc

    def list_packages(self) -> List[SkillPackage]:
        return sorted(self._packages.values(), key=lambda p: (p.skill_id, p.version))


@dataclass
class Agent:
    agent_id: str
    specialty: str
    local_evaluations: Dict[str, Evaluation] = field(default_factory=dict)

    def review_shared_skill(
        self,
        package: SkillPackage,
        *,
        min_trials: int = 20,
        min_success_rate: float = 0.80,
        max_regression_rate: float = 0.05,
    ) -> bool:
        """Accept as verified only when both source evidence and receiver replay pass."""
        package.validate()
        receiver = self.local_evaluations.get(package.skill_id)
        source = package.evaluation
        passed = (
            source.environment == "mujoco-simulation"
            and source.trials >= min_trials
            and source.success_rate >= min_success_rate
            and source.regression_rate <= max_regression_rate
            and receiver is not None
            and receiver.valid()
            and receiver.trials >= min_trials
            and receiver.success_rate >= min_success_rate
            and receiver.regression_rate <= max_regression_rate
            and receiver.environment == "mujoco-simulation"
        )
        package.reviewers.append(self.agent_id)
        if passed:
            package.state = SkillState.VERIFIED
            package.notes.append(f"Receiver replay passed on {self.agent_id}.")
        else:
            package.state = SkillState.REJECTED
            package.notes.append(f"Receiver replay or evidence threshold failed on {self.agent_id}.")
        return passed


def request_human_promotion(package: SkillPackage, *, human_approved: bool) -> bool:
    """Mark eligible packages for human review; never deploys or commands hardware."""
    package.validate()
    e = package.evaluation
    if package.state is not SkillState.VERIFIED:
        return False
    if e.environment != "mujoco-simulation" or e.trials < 20 or e.success_rate < 0.80 or e.regression_rate > 0.05:
        return False
    if not human_approved:
        package.notes.append("Human promotion approval not granted; remains simulation-only.")
        return False
    package.state = SkillState.APPROVED_FOR_REVIEW
    package.notes.append("Human approved progression to a separate supervised validation review; no deployment performed.")
    return True
