from __future__ import annotations

import uuid
from dataclasses import dataclass
import cv2

from .models import AnalysisResult, TraceStep
from .trust import TrustInputs, calculate_vcts, decide_action
from .vision import (
    FrameObservation,
    analyze_video,
    detect_motion,
    enhance_pair,
    image_quality,
    select_verification_tool,
    stress_test_pair,
    summarize_stress,
)


@dataclass
class AgentOutcome:
    result: AnalysisResult


def _trace(steps: list[TraceStep], stage: str, message: str, **data) -> None:
    steps.append(TraceStep(step=len(steps) + 1, stage=stage, message=message, data=data))


def run_agent(video_path: str, source_name: str) -> AgentOutcome:
    trace_id = str(uuid.uuid4())
    steps: list[TraceStep] = []
    observations = analyze_video(video_path)
    _trace(steps, "PERCEPTION", "OpenCV 5 processed the video stream and produced frame-level visual evidence.", observations=len(observations))

    candidates = [o for o in observations if o.evidence.present and o.evidence.in_restricted_zone]
    if not candidates:
        _trace(steps, "DECISION", "No motion evidence entered the configured restricted zone.", decision="IGNORE")
        _trace(steps, "ACTION", "No alert was raised; the system remains in observation mode.", action="IGNORE")
        return AgentOutcome(
            AnalysisResult(
                trace_id=trace_id,
                opencv_version=cv2.__version__,
                opencv5_compliant=cv2.__version__.split(".")[0] == "5",
                source=source_name,
                frame_index=None,
                quality=None,
                evidence=None,
                vcts=None,
                initial_action="IGNORE",
                final_action="IGNORE",
                trace=steps,
                limitations=["Motion-based MVP: it detects scene change, not human identity or semantic intent."],
            )
        )

    # Use the strongest zone event so the demo is deterministic and the evidence is inspectable.
    obs: FrameObservation = max(candidates, key=lambda o: o.evidence.confidence * (0.5 + 0.5 * o.temporal_consistency))
    stress = stress_test_pair(obs.prev_frame, obs.frame, obs.evidence)
    robustness = summarize_stress(stress)
    inputs = TrustInputs(
        detection=obs.evidence.confidence,
        image_quality=obs.quality.overall,
        temporal_consistency=obs.temporal_consistency,
        stress_robustness=robustness,
        geometry_consistency=obs.geometry_consistency,
    )
    vcts = calculate_vcts(inputs)
    initial_action = decide_action(vcts.score, True)
    _trace(
        steps,
        "PERCEPTION",
        "Restricted-zone motion was detected and stress-tested with OpenCV transformations.",
        frame_index=obs.frame_index,
        detection_confidence=obs.evidence.confidence,
        stress_robustness=robustness,
        vcts=vcts.score,
    )
    _trace(steps, "DECISION", "The VCTS policy selected the next action from calibrated visual evidence.", action=initial_action, vcts=vcts.score)

    final_action = initial_action
    selected_tool = None
    requires_human = False

    if initial_action in {"VERIFY", "RE_OBSERVE"}:
        selected_tool = select_verification_tool(obs.quality, robustness)
        _trace(
            steps,
            "TOOL_CALL",
            "The agent selected an additional OpenCV verification tool because the first perception was not sufficiently trusted.",
            tool=selected_tool,
            reason={
                "brightness": obs.quality.brightness,
                "contrast": obs.quality.contrast,
                "sharpness": obs.quality.sharpness,
                "robustness": robustness,
            },
        )
        p2, f2 = enhance_pair(obs.prev_frame, obs.frame, selected_tool)
        q2 = image_quality(f2)
        ev2 = detect_motion(p2, f2)
        stress2 = stress_test_pair(p2, f2, ev2)
        robust2 = summarize_stress(stress2)
        vcts2 = calculate_vcts(
            TrustInputs(
                detection=ev2.confidence,
                image_quality=q2.overall,
                temporal_consistency=obs.temporal_consistency,
                stress_robustness=robust2,
                geometry_consistency=obs.geometry_consistency,
            )
        )
        _trace(
            steps,
            "PERCEPTION",
            "OpenCV re-analysis produced new evidence after the agent tool call.",
            tool=selected_tool,
            in_restricted_zone=ev2.in_restricted_zone,
            detection_confidence=ev2.confidence,
            vcts=vcts2.score,
        )
        if ev2.in_restricted_zone and vcts2.score >= 80 and robustness >= 0.70:
            final_action = "ACT"
            vcts = vcts2
            obs.evidence = ev2
            obs.quality = q2
            stress = stress2
        else:
            final_action = "HUMAN_REVIEW"
            requires_human = True
            vcts = vcts2
            obs.evidence = ev2
            obs.quality = q2
            stress = stress2
            _trace(
                steps,
                "HUMAN_CONTROL",
                "The re-analysis did not reach the confidence gate. The agent requested explicit human approval instead of acting autonomously.",
                threshold=80,
                observed_vcts=vcts2.score,
                initial_stress_robustness=robustness,
                minimum_stress_robustness=0.70,
            )
    elif initial_action == "HUMAN_REVIEW":
        requires_human = True
        _trace(
            steps,
            "HUMAN_CONTROL",
            "The initial visual evidence was below the autonomous-action threshold, so human review is mandatory.",
            observed_vcts=vcts.score,
        )

    if final_action == "ACT":
        _trace(steps, "ACTION", "Alert action authorized from visual evidence.", action="ACT")
    elif final_action == "HUMAN_REVIEW":
        _trace(steps, "ACTION", "Autonomous alert is withheld pending human approval.", action="HUMAN_REVIEW")

    limitations = [
        "The MVP uses motion and geometric evidence, not biometric identification or intent classification.",
        "VCTS thresholds are research/demo defaults and require domain calibration before safety-critical deployment.",
        "Stress tests approximate common degradation modes; they are not a complete adversarial-vision threat model.",
        "A single fixed camera and rectangular restricted zone are assumed in the reference implementation.",
    ]
    return AgentOutcome(
        AnalysisResult(
            trace_id=trace_id,
            opencv_version=cv2.__version__,
            opencv5_compliant=cv2.__version__.split(".")[0] == "5",
            source=source_name,
            frame_index=obs.frame_index,
            quality=obs.quality,
            evidence=obs.evidence,
            stress_tests=stress,
            vcts=vcts,
            initial_action=initial_action,
            final_action=final_action,
            selected_tool=selected_tool,
            requires_human_approval=requires_human,
            trace=steps,
            limitations=limitations,
        )
    )
