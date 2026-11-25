
from app.models.rca_report import RCAReport


class HypothesisAnalyzer:
    """
    Consolidates overlapping RCA hypotheses.

    This component identifies duplicate explanations; it does not
    establish causal relationships or increase confidence.
    """

    CONFIDENCE_ORDER = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    def _shared_evidence_ids(self, first, second) -> set[str]:
        first_ids = {
            evidence.evidence_id
            for evidence in first.supporting_evidence
        }

        second_ids = {
            evidence.evidence_id
            for evidence in second.supporting_evidence
        }

        return first_ids & second_ids

    def _can_merge(self, first, second) -> bool:
        """
        Merge only when both hypotheses share:
        1. At least one supporting evidence reference.
        2. At least one related database.

        This is deliberately conservative.
        """

        shared_evidence = self._shared_evidence_ids(first, second)
        shared_databases = (
            set(first.related_databases)
            & set(second.related_databases)
        )

        return bool(shared_evidence and shared_databases)

    def _merge_unique_strings(self, first, second) -> list[str]:
        return list(dict.fromkeys(first + second))

    def _merge_evidence(self, first, second):
        """
        Deduplicate evidence by evidence ID.

        One incident should not appear multiple times merely because
        the LLM generated different descriptions for it.
        """
        merged = []
        seen = set()

        for evidence in (
            first.supporting_evidence
            + second.supporting_evidence
        ):
            if evidence.evidence_id not in seen:
                seen.add(evidence.evidence_id)
                merged.append(evidence)

        return merged

    def _merge_confidence(self, first, second) -> str:
        """
        Retain the lower confidence level.
        Consolidation must never increase confidence.
        """

        if (
            self.CONFIDENCE_ORDER[first.confidence]
            <= self.CONFIDENCE_ORDER[second.confidence]
        ):
            return first.confidence

        return second.confidence

    def _merge_hypotheses(self, first, second):
        # Prefer the more descriptive title.
        title = (
            first.title
            if len(first.title) >= len(second.title)
            else second.title
        )

        # Preserve both explanations rather than inventing
        # a stronger causal statement.
        descriptions = list(dict.fromkeys([
            first.description.strip(),
            second.description.strip()
        ]))

        description = " ".join(descriptions)

        confidence = self._merge_confidence(first, second)

        confidence_reason = (
            f"Consolidated from overlapping hypotheses. "
            f"Confidence retained at {confidence}; "
            f"consolidation does not increase confidence. "
            f"Original assessments: "
            f"{first.confidence} and {second.confidence}. "
            f"Assessment details: "
            f"{first.confidence_reason} "
            f"{second.confidence_reason}"
        )

        merged = first.model_copy(deep=True)

        merged.title = title
        merged.description = description
        merged.confidence = confidence
        merged.confidence_reason = confidence_reason

        merged.supporting_evidence = self._merge_evidence(
            first,
            second
        )

        merged.contradicting_or_missing_evidence = (
            self._merge_unique_strings(
                first.contradicting_or_missing_evidence,
                second.contradicting_or_missing_evidence
            )
        )

        merged.related_services = self._merge_unique_strings(
            first.related_services,
            second.related_services
        )

        merged.related_databases = self._merge_unique_strings(
            first.related_databases,
            second.related_databases
        )

        merged.related_deployments = self._merge_unique_strings(
            first.related_deployments,
            second.related_deployments
        )

        merged.recommended_validation_steps = (
            self._merge_unique_strings(
                first.recommended_validation_steps,
                second.recommended_validation_steps
            )
        )

        merged.validation_warnings = self._merge_unique_strings(
            first.validation_warnings,
            second.validation_warnings
        )

        merged.validation_warnings.append(
            "This hypothesis was consolidated with another "
            "hypothesis sharing supporting evidence and a database. "
            "The consolidation does not establish causality."
        )

        merged.validation_warnings = list(
            dict.fromkeys(merged.validation_warnings)
        )

        return merged

    def analyze(self, report: RCAReport) -> RCAReport:
        """
        Consolidate overlapping hypotheses while preserving order.
        """

        hypotheses = [
            hypothesis.model_copy(deep=True)
            for hypothesis in report.root_cause_hypotheses
        ]

        consolidated = []

        for hypothesis in hypotheses:
            merged = False

            for index, existing in enumerate(consolidated):
                if self._can_merge(existing, hypothesis):
                    consolidated[index] = self._merge_hypotheses(
                        existing,
                        hypothesis
                    )
                    merged = True
                    break

            if not merged:
                consolidated.append(hypothesis)

        report.root_cause_hypotheses = consolidated

        return report
