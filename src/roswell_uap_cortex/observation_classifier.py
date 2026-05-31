"""Deterministic observation-vs-interpretation classification."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import ExtractedObservation, ObservationType, RawInputType


DIRECT_MARKERS = {
    "observed",
    "saw",
    "seen",
    "heard",
    "recorded",
    "measured",
    "photographed",
    "detected",
    "noted",
}
INTERPRETATION_MARKERS = {
    "therefore",
    "identified as",
    "concluded",
    "interpreted",
    "explained as",
    "classified as",
    "was an aircraft",
    "was a balloon",
}
SPECULATION_MARKERS = {
    "may",
    "might",
    "could",
    "possibly",
    "probably",
    "speculate",
    "speculative",
    "unknown craft",
    "non-human",
}
REPORTED_MARKERS = {
    "witness stated",
    "witness reported",
    "according to",
    "claimed",
    "reported that",
    "said that",
    "source said",
}
METADATA_MARKERS = {
    "source:",
    "title:",
    "date:",
    "author:",
    "collected at",
    "metadata",
}


@dataclass(slots=True)
class ObservationClassifier:
    """Classify extracted spans without deciding whether they are true."""

    def classify(self, observation: ExtractedObservation, input_type: RawInputType | str | None = None) -> ExtractedObservation:
        text = observation.text.casefold()
        interpretation = self._markers(text, INTERPRETATION_MARKERS)
        speculation = self._markers(text, SPECULATION_MARKERS)
        reported = self._markers(text, REPORTED_MARKERS)
        direct = self._markers(text, DIRECT_MARKERS)
        metadata = self._markers(text, METADATA_MARKERS)

        observation.interpretation_markers = interpretation
        observation.speculation_markers = speculation
        observation.reported_speech_markers = reported

        if isinstance(input_type, str):
            input_type = RawInputType(input_type)

        if input_type in {RawInputType.IMAGE_METADATA, RawInputType.VIDEO_METADATA} or metadata:
            observation.observation_type = ObservationType.METADATA_STATEMENT
            observation.classification_notes.append("metadata-like span; not treated as direct observation")
        elif speculation:
            observation.observation_type = ObservationType.SPECULATION
            observation.classification_notes.append("speculation markers preserved")
        elif reported:
            observation.observation_type = ObservationType.REPORTED_CLAIM
            observation.classification_notes.append("reported speech preserved as claim report")
        elif interpretation:
            observation.observation_type = ObservationType.INTERPRETATION
            observation.classification_notes.append("interpretation markers preserved")
        elif direct:
            observation.observation_type = ObservationType.DIRECT_OBSERVATION
            observation.classification_notes.append("direct observation markers present")
        else:
            observation.observation_type = ObservationType.UNKNOWN
            observation.classification_notes.append("no deterministic observation classification marker")

        marker_family_count = sum(
            1
            for present in (interpretation, speculation, reported, direct, metadata)
            if present
        )
        if marker_family_count > 1:
            observation.classification_notes.append("mixed markers present; strongest cautionary type selected")
        return observation

    def _markers(self, text: str, markers: set[str]) -> list[str]:
        return sorted(marker for marker in markers if marker in text)
