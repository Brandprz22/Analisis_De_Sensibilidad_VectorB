import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
        /* Layout general */
        .block-container {
            padding-top: 2.0rem;
            padding-bottom: 2.0rem;
            padding-left: 2.0rem;
            padding-right: 2.0rem;
            max-width: 950px;
        }

        .katex {
            font-size: 1.05em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
