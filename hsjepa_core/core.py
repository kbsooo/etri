#!/usr/bin/env python3
"""Reference implementation of the competition-agnostic HS-JEPA core.

This module intentionally knows nothing about any dataset schema, target name,
scoreboard, or output file format. It implements the reusable mechanism:

partial human context -> hidden state -> listener responsibility
-> action health -> invariant-preserving release.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable


Vector = tuple[float, ...]


@dataclass(frozen=True)
class ContextView:
    """A partial view of a person-state context."""

    name: str
    embedding: Vector
    coverage: float = 1.0
    uncertainty: float = 0.0
    mask_family: str = "semantic"


@dataclass(frozen=True)
class ListenerPrototype:
    """A downstream listener that may react to the same hidden state."""

    name: str
    embedding: Vector
    sensitivity: float = 1.0


@dataclass(frozen=True)
class CandidateAction:
    """A bounded output move proposed by an adapter."""

    name: str
    listener: str
    delta_embedding: Vector
    amplitude: float
    support: float = 1.0


@dataclass(frozen=True)
class HiddenStatePrediction:
    state: Vector
    prediction_energy: float
    context_coverage: float
    context_disagreement: float


@dataclass(frozen=True)
class ActionDecision:
    action: CandidateAction
    listener_responsibility: float
    listener_alignment: float
    invariant_energy_delta: float
    health_score: float
    released: bool

    def to_json(self) -> dict[str, object]:
        return asdict(self)


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(a: Vector) -> float:
    return math.sqrt(max(0.0, dot(a, a)))


def add(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def scale(a: Vector, value: float) -> Vector:
    return tuple(value * x for x in a)


def distance(a: Vector, b: Vector) -> float:
    return norm(tuple(x - y for x, y in zip(a, b)))


def normalize(a: Vector) -> Vector:
    length = norm(a)
    if length <= 1e-12:
        return tuple(0.0 for _ in a)
    return tuple(x / length for x in a)


def cosine(a: Vector, b: Vector) -> float:
    denom = norm(a) * norm(b)
    if denom <= 1e-12:
        return 0.0
    return dot(a, b) / denom


def softmax(scores: dict[str, float], temperature: float) -> dict[str, float]:
    if not scores:
        return {}
    tau = max(temperature, 1e-6)
    peak = max(scores.values())
    exp_scores = {key: math.exp((value - peak) / tau) for key, value in scores.items()}
    total = sum(exp_scores.values())
    if total <= 1e-12:
        weight = 1.0 / len(scores)
        return {key: weight for key in scores}
    return {key: value / total for key, value in exp_scores.items()}


class HSJEPACore:
    """Small executable core for HS-JEPA-style reasoning."""

    def __init__(
        self,
        responsibility_temperature: float = 0.35,
        health_release_threshold: float = 0.06,
        invariant_release_threshold: float = 0.45,
    ) -> None:
        self.responsibility_temperature = responsibility_temperature
        self.health_release_threshold = health_release_threshold
        self.invariant_release_threshold = invariant_release_threshold

    def predict_hidden_state(self, contexts: Iterable[ContextView]) -> HiddenStatePrediction:
        views = list(contexts)
        if not views:
            raise ValueError("at least one context view is required")
        dim = len(views[0].embedding)
        if any(len(view.embedding) != dim for view in views):
            raise ValueError("all context embeddings must have the same dimension")

        weights = [max(0.0, view.coverage) * max(0.0, 1.0 - view.uncertainty) for view in views]
        if sum(weights) <= 1e-12:
            weights = [1.0 for _ in views]
        total = sum(weights)
        raw_state = tuple(
            sum(weight * view.embedding[idx] for weight, view in zip(weights, views)) / total
            for idx in range(dim)
        )
        state = normalize(raw_state)
        disagreement = sum(weight * distance(normalize(view.embedding), state) for weight, view in zip(weights, views)) / total
        coverage = sum(max(0.0, min(1.0, view.coverage)) for view in views) / len(views)
        uncertainty = sum(max(0.0, min(1.0, view.uncertainty)) for view in views) / len(views)
        prediction_energy = disagreement + 0.5 * (1.0 - coverage) + 0.5 * uncertainty
        return HiddenStatePrediction(
            state=state,
            prediction_energy=prediction_energy,
            context_coverage=coverage,
            context_disagreement=disagreement,
        )

    def listener_responsibility(
        self,
        hidden: HiddenStatePrediction,
        listeners: Iterable[ListenerPrototype],
    ) -> dict[str, float]:
        scores = {
            item.name: item.sensitivity * cosine(hidden.state, normalize(item.embedding))
            for item in listeners
        }
        return softmax(scores, self.responsibility_temperature)

    def invariant_energy_delta(
        self,
        hidden: HiddenStatePrediction,
        action: CandidateAction,
        invariant_anchors: Iterable[Vector] | None = None,
    ) -> float:
        post_state = normalize(add(hidden.state, scale(action.delta_embedding, action.amplitude)))
        if invariant_anchors:
            anchors = [normalize(anchor) for anchor in invariant_anchors]
            return min(distance(post_state, anchor) for anchor in anchors)
        return distance(post_state, hidden.state)

    def score_action(
        self,
        hidden: HiddenStatePrediction,
        listeners: Iterable[ListenerPrototype],
        responsibilities: dict[str, float],
        action: CandidateAction,
        invariant_anchors: Iterable[Vector] | None = None,
    ) -> ActionDecision:
        listener_map = {item.name: item for item in listeners}
        if action.listener not in listener_map:
            raise KeyError(f"unknown listener: {action.listener}")
        listener = listener_map[action.listener]
        responsibility = responsibilities.get(action.listener, 0.0)
        alignment = max(0.0, cosine(action.delta_embedding, normalize(listener.embedding)))
        invariant_delta = self.invariant_energy_delta(hidden, action, invariant_anchors)
        amplitude_penalty = 1.0 + abs(action.amplitude) + hidden.prediction_energy + invariant_delta
        health = max(0.0, action.support) * responsibility * alignment / amplitude_penalty
        released = health >= self.health_release_threshold and invariant_delta <= self.invariant_release_threshold
        return ActionDecision(
            action=action,
            listener_responsibility=responsibility,
            listener_alignment=alignment,
            invariant_energy_delta=invariant_delta,
            health_score=health,
            released=released,
        )

    def release_actions(
        self,
        contexts: Iterable[ContextView],
        listeners: Iterable[ListenerPrototype],
        actions: Iterable[CandidateAction],
        invariant_anchors: Iterable[Vector] | None = None,
    ) -> dict[str, object]:
        listener_list = list(listeners)
        hidden = self.predict_hidden_state(contexts)
        responsibilities = self.listener_responsibility(hidden, listener_list)
        decisions = [
            self.score_action(hidden, listener_list, responsibilities, action, invariant_anchors)
            for action in actions
        ]
        return {
            "hidden": asdict(hidden),
            "responsibilities": responsibilities,
            "decisions": [item.to_json() for item in decisions],
            "released_actions": [item.action.name for item in decisions if item.released],
        }
