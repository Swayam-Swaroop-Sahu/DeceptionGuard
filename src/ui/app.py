"""
DeceptionGuard Streamlit UI
Single-email scan workflow moved from CLI to a paste-box UI.
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables (same as CLI)
load_dotenv()

# Import pipeline components
from src.ingestion.parser import parse_eml_string, ParseError
from src.intent_graph.extractor import extract_intent_graph
from src.risk_engine.scorer import score_graph


def render_factor_table(result):
    """Render factor breakdown as a table."""
    import pandas as pd
    
    data = []
    for factor in result.factors:
        status = "✅ TRIGGERED" if factor.contribution > 0 else "⬜ Not triggered"
        data.append({
            "Factor": factor.name.replace("_", " ").title(),
            "Weight": factor.weight,
            "Contribution": factor.contribution,
            "Status": status
        })
    
    df = pd.DataFrame(data)
    st.table(df)


def render_risk_level(score: int):
    """Render risk level with colored indicator."""
    if score >= 70:
        st.error(f"🔴 **Risk Level: HIGH** ({score}/100)")
    elif score >= 40:
        st.warning(f"🟠 **Risk Level: MEDIUM** ({score}/100)")
    elif score > 0:
        st.info(f"🟡 **Risk Level: LOW** ({score}/100)")
    else:
        st.success(f"🟢 **Risk Level: MINIMAL** ({score}/100)")


def render_intent_graph(graph: dict):
    """Render intent graph summary."""
    st.subheader("Intent Graph Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Claimed Identity:** {graph['claimed_identity'] or '(none detected)'}")
        st.markdown(f"**Requested Action:** {graph['requested_action'] or '(none detected)'}")
    
    with col2:
        urgency = graph['urgency_signals']
        authority = graph['authority_signals']
        payload = graph['payload_targets']
        
        st.markdown(f"**Urgency Signals:** {', '.join(urgency) if urgency else '(none)'}")
        st.markdown(f"**Authority Signals:** {', '.join(authority) if authority else '(none)'}")
    
    if payload:
        st.markdown("**Payload Targets:**")
        for target in payload:
            st.markdown(f"- {target}")


def main():
    st.set_page_config(
        page_title="DeceptionGuard",
        page_icon="🛡️",
        layout="wide"
    )
    
    st.title("🛡️ DeceptionGuard — Email Security Analyzer")
    st.caption("Paste a raw email (.eml content) below to analyze for phishing indicators.")
    
    # Text area for pasting email content
    raw_email = st.text_area(
        "Raw Email Content",
        height=300,
        placeholder="Paste the full raw email here (headers + body)...\n\nExample:\nFrom: sender@example.com\nSubject: Test\n\nHello world...",
        help="Paste the complete raw email including headers (From, Subject, Date, etc.) and body."
    )
    
    analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    if analyze_clicked:
        if not raw_email or not raw_email.strip():
            st.error("Please paste an email to analyze.")
            return
        
        with st.spinner("Analyzing email..."):
            try:
                # Step 1: Parse email
                record = parse_eml_string(raw_email)
                
                # Step 2: Extract intent graph
                graph = extract_intent_graph(record)
                
                # Step 3: Score risk
                result = score_graph(graph)
                
                # Render results
                st.divider()
                st.subheader("📊 Analysis Results")
                
                # Basic email info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Sender:** {record.sender}")
                    st.markdown(f"**Subject:** {record.subject or '(no subject)'}")
                with col2:
                    st.markdown(f"**Date:** {record.date or '(unknown)'}")
                
                # Risk score as big metric
                st.metric("Risk Score", f"{result.total_score}/100")
                
                # Risk level with color
                render_risk_level(result.total_score)
                
                # Factor breakdown
                st.subheader("Factor Breakdown")
                render_factor_table(result)
                
                # Links found
                if record.links:
                    st.subheader("Links Found")
                    for link in record.links:
                        st.markdown(f"- {link}")
                else:
                    st.subheader("Links Found")
                    st.markdown("(none)")
                
                # Intent graph
                render_intent_graph(graph)
                
            except ParseError as e:
                st.error(f"❌ Failed to parse email: {e}")
                st.caption("Make sure you pasted a valid email with at least a 'From' header.")
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                # In development, show traceback
                if st.checkbox("Show technical details"):
                    import traceback
                    st.code(traceback.format_exc())


if __name__ == "__main__":
    main()