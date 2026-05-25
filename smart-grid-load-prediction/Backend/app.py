import streamlit as st
from login import login_page
from dashboard import dashboard
from signup import signup_page

def main():
    st.set_page_config(page_title="Energy Forecasting", layout="wide")

    # session init
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "show_signup" not in st.session_state:
        st.session_state["show_signup"] = False

    # routing
    if st.session_state["logged_in"]:
        dashboard()

    elif st.session_state["show_signup"]:
        signup_page()

    else:
        login_page()

if __name__ == "__main__":
    main()