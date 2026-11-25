
import os

import requests
import streamlit as st


API_URL = os.getenv(
    "RCA_API_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="Incident RCA Assistant",
    page_icon="🔍",
    layout="wide"
)


st.title("🔍 Incident RCA Assistant")

st.caption(
    "Enterprise incident investigation powered by "
    "Hybrid Retrieval, Neo4j GraphRAG and LLM-based RCA."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Investigation Settings")

top_k = st.sidebar.slider(
    "Vector search results",
    min_value=1,
    max_value=20,
    value=5
)

max_hops = st.sidebar.slider(
    "Graph traversal depth",
    min_value=1,
    max_value=5,
    value=3
)

st.sidebar.markdown("---")

st.sidebar.caption(
    f"Backend API: {API_URL}"
)


# --------------------------------------------------
# Investigation input
# --------------------------------------------------

st.subheader("Start an Investigation")

query = st.text_area(
    "Describe the incident or ask a question",
    value="Why are payment requests timing out?",
    height=100,
    placeholder="Example: Why is the Payment API experiencing elevated latency?"
)

investigate = st.button(
    "Run Investigation",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# API invocation
# --------------------------------------------------

if investigate:

    if not query.strip():
        st.warning("Please enter an investigation question.")

    else:

        payload = {
            "query": query,
            "top_k": top_k,
            "max_hops": max_hops
        }

        try:
            with st.spinner(
                "Investigating incidents, traversing the graph "
                "and generating RCA hypotheses..."
            ):

                response = requests.post(
                    f"{API_URL}/api/investigations",
                    json=payload,
                    timeout=300
                )

                response.raise_for_status()

                result = response.json()

                st.session_state["investigation_result"] = result

        except requests.exceptions.ConnectionError:
            st.error(
                "Unable to connect to the FastAPI backend. "
                "Please check whether the API server is running."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The investigation request timed out. "
                "Please try again."
            )

        except requests.exceptions.HTTPError as exc:
            st.error(
                f"Investigation API returned an error: {exc}"
            )

        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")


# --------------------------------------------------
# Display investigation results
# --------------------------------------------------

result = st.session_state.get("investigation_result")


if result:

    report = result.get("report", {})
    context = result.get("context_summary", {})

    st.markdown("---")

    st.header("Investigation Results")

    st.markdown(
        f"**Question:** {result.get('query', '')}"
    )

    # ----------------------------------------------
    # Overview metrics
    # ----------------------------------------------

    st.subheader("Investigation Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Primary Incident",
        result.get("primary_incident_id") or "N/A"
    )

    col2.metric(
        "Incidents",
        context.get("incident_count", 0)
    )

    col3.metric(
        "Graph Paths",
        context.get("graph_path_count", 0)
    )

    col4.metric(
        "Historical Evidence",
        context.get("ranked_evidence_count", 0)
    )

    # ----------------------------------------------
    # Incident summary
    # ----------------------------------------------

    st.subheader("Incident Summary")

    st.info(
        report.get(
            "incident_summary",
            "No incident summary available."
        )
    )

    st.markdown("**Impact**")

    st.write(
        report.get(
            "impact_summary",
            "No impact summary available."
        )
    )

    # ----------------------------------------------
    # Service classification
    # ----------------------------------------------

    st.subheader("Service Impact")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Directly Impacted**")

        for service in report.get(
            "directly_impacted_services", []
        ):
            st.write(f"🔴 {service}")

    with col2:
        st.markdown("**Suspected Contributors**")

        for service in report.get(
            "suspected_contributing_services", []
        ):
            st.write(f"🟠 {service}")

    with col3:
        st.markdown("**Requires Investigation**")

        for service in report.get(
            "services_requiring_investigation", []
        ):
            st.write(f"🔵 {service}")

    # ----------------------------------------------
    # Root cause hypotheses
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Root Cause Hypotheses")

    hypotheses = report.get(
        "root_cause_hypotheses", []
    )

    for index, hypothesis in enumerate(hypotheses, 1):

        confidence = hypothesis.get(
            "confidence", "LOW"
        )

        with st.expander(
            f"{index}. {hypothesis.get('title', 'Untitled')} "
            f"— {confidence} confidence",
            expanded=(index == 1)
        ):

            st.markdown("**Description**")

            st.write(
                hypothesis.get("description", "")
            )

            st.markdown("**Confidence reasoning**")

            st.write(
                hypothesis.get("confidence_reason", "")
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Related Services**")

                st.write(
                    hypothesis.get("related_services", [])
                )

                st.markdown("**Related Databases**")

                st.write(
                    hypothesis.get("related_databases", [])
                )

                st.markdown("**Related Deployments**")

                st.write(
                    hypothesis.get("related_deployments", [])
                )

            with col2:
                st.markdown("**Supporting Evidence**")

                for evidence in hypothesis.get(
                    "supporting_evidence", []
                ):
                    st.write(
                        f"- {evidence.get('evidence_id')}: "
                        f"{evidence.get('description')}"
                    )

            st.markdown("**Missing or Contradicting Evidence**")

            missing = hypothesis.get(
                "contradicting_or_missing_evidence", []
            )

            if missing:
                for item in missing:
                    st.write(f"- {item}")
            else:
                st.write("None reported.")

            st.markdown("**Recommended Validation Steps**")

            for step in hypothesis.get(
                "recommended_validation_steps", []
            ):
                st.write(f"- {step}")

            warnings = hypothesis.get(
                "validation_warnings", []
            )

            if warnings:
                st.warning(
                    "\n".join(f"- {warning}" for warning in warnings)
                )

    # ----------------------------------------------
    # Investigation steps
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Recommended Investigation Steps")

    for step in report.get("investigation_steps", []):
        st.write(f"- {step}")

    # ----------------------------------------------
    # Timeline
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Incident and Deployment Timeline")

    timeline = result.get("timeline", [])

    if timeline:

        for event in timeline:

            timestamp = event.get("timestamp", "")
            event_type = event.get("event_type", "")
            event_id = event.get("event_id", "")
            description = event.get("description", "")

            with st.container(border=True):

                st.markdown(
                    f"**{timestamp} | {event_type} | {event_id}**"
                )

                st.write(description)

                if event.get("service_name"):
                    st.caption(
                        f"Service: {event['service_name']}"
                    )

    else:
        st.info("No timeline events available.")

    # ----------------------------------------------
    # Ranked historical evidence
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Ranked Historical Evidence")

    evidence = result.get("ranked_evidence", [])

    if evidence:

        for item in evidence:

            with st.container(border=True):

                st.markdown(
                    f"**{item.get('incident_id')} — "
                    f"{item.get('title')}**"
                )

                st.write(
                    f"Relevance score: {item.get('total_score')}"
                )

                st.write(
                    f"Shared services: "
                    f"{', '.join(item.get('shared_services', []))}"
                )

                st.caption(
                    "; ".join(item.get("ranking_reasons", []))
                )

    else:
        st.info("No ranked historical evidence available.")

    # ----------------------------------------------
    # Related incidents
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Related Incidents")

    for item in result.get("related_incidents", []):

        st.write(
            f"**{item.get('source_incident')}** → "
            f"{item.get('shared_service')} → "
            f"**{item.get('related_incident')}** "
            f"({item.get('related_incident_title')})"
        )

    # ----------------------------------------------
    # Caveats and warnings
    # ----------------------------------------------

    st.markdown("---")
    st.subheader("Caveats and Validation Warnings")

    caveats = report.get("overall_caveats", [])
    warnings = report.get("validation_warnings", [])

    for caveat in caveats:
        st.info(caveat)

    for warning in warnings:
        st.warning(warning)

    # ----------------------------------------------
    # Raw JSON
    # ----------------------------------------------

    with st.expander("View Complete JSON Response"):
        st.json(result)
