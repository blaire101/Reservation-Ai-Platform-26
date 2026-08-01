import streamlit as st
from app.graph import ask

st.set_page_config(page_title="Reservation Intelligence", layout="wide")
st.title("Reservation Intelligence Data & AI Platform")
st.caption("Reservation → Order → Final Payment Status")

examples = [
    "What is the grain of the reservation conversion mart?",
    "Show paid conversion rate by site.",
    "Which campaign has the lowest paid conversion rate?",
    "Why is the Singapore reservation dashboard incomplete on 2026-07-31?",
]
question = st.selectbox("Example", examples)
custom = st.text_input("Or ask your own question", "")
if st.button("Ask"):
    result = ask(custom or question)
    st.subheader(result.answer)
    st.write("Route:", result.route)
    if result.evidence:
        with st.expander("Sources"):
            for e in result.evidence:
                st.markdown(f"**{e.source}**")
                st.write(e.excerpt)
    if result.data:
        with st.expander("Tool output"):
            st.json(result.data)
    if result.warnings:
        st.warning("\n".join(result.warnings))
