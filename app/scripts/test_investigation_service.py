
from app.investigation.investigation_service import InvestigationService


def main():
    service = InvestigationService()

    try:
        result = service.investigate(
            query="Why are payment requests timing out?",
            top_k=5,
            max_hops=3
        )

        print("\n========== INVESTIGATION RESULT ==========")

        print("Primary incident:", result["primary_incident_id"])

        print("\nContext summary:")
        print(result["context_summary"])

        print("\nValidated RCA report:")
        print(result["report"])

        print("\nTimeline events:", len(result["timeline"]))

        print(
            "Ranked evidence:",
            len(result["ranked_evidence"])
        )

        print(
            "Related incidents:",
            len(result["related_incidents"])
        )

    finally:
        service.close()


if __name__ == "__main__":
    main()
