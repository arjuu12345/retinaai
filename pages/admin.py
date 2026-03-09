import streamlit as st
import os
import sys

# Fix import path for Streamlit pages
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_db,
    get_pending,
    get_approved,
    approve,
    delete_appointment,
    get_patient_reports
)

# Initialize database
init_db()

# Page Configuration
st.set_page_config(page_title="Admin Dashboard", page_icon="🏥", layout="wide")

# -----------------------------
# Authentication
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# -----------------------------
# Login Section
# -----------------------------
if not st.session_state.authenticated:

    st.title("🏥 Admin Access")

    with st.container():
        col1, col2 = st.columns([1,2])

        with col1:
            password = st.text_input("Enter Admin Password", type="password")

            if st.button("Login"):
                if password == "admin123":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid Password")

    st.stop()


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("⚙️ Control Panel")

    search_query = st.text_input("🔍 Search Patient", "").lower()

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()


# -----------------------------
# Main Dashboard
# -----------------------------
st.title("🏥 Admin Management Dashboard")

tab1, tab2 = st.tabs(["⏳ Pending Requests", "✅ Approved Appointments"])


# =============================
# TAB 1 : Pending Appointments
# =============================
with tab1:

    pending = get_pending()

    if pending:

        filtered_pending = [
            a for a in pending
            if search_query in a[1].lower()
        ]

        if filtered_pending:

            for appt in filtered_pending:

                with st.expander(f"Patient: {appt[1]} | Date: {appt[3]}", expanded=True):

                    col1, col2, col3 = st.columns([2,1,1])

                    col1.write(f"**Doctor:** {appt[2]}")

                    if col2.button("Approve ✅", key=f"approve_{appt[0]}"):
                        approve(appt[0])
                        st.success("Appointment Approved")
                        st.rerun()

                    if col3.button("Delete 🗑️", key=f"delete_pending_{appt[0]}"):
                        delete_appointment(appt[0])
                        st.warning("Appointment Deleted")
                        st.rerun()

        else:
            st.info("No matching pending appointments.")

    else:
        st.info("No pending appointments.")


# =============================
# TAB 2 : Approved Appointments
# =============================
with tab2:

    approved = get_approved()

    if approved:

        filtered_approved = [
            a for a in approved
            if search_query in a[1].lower()
        ]

        if filtered_approved:

            for appt in filtered_approved:

                with st.expander(f"Patient: {appt[1]} | Date: {appt[3]}"):

                    col1, col2, col3 = st.columns([2,1,1])

                    col1.write(f"**Doctor:** {appt[2]}")

                    # -------------------------
                    # Report Download
                    # -------------------------
                    reports = get_patient_reports(appt[1])

                    if reports and os.path.exists(reports[0][4]):

                        with open(reports[0][4], "rb") as f:

                            col2.download_button(
                                "Download 📄",
                                data=f,
                                file_name=os.path.basename(reports[0][4]),
                                key=f"download_{appt[0]}"
                            )

                    else:
                        col2.write("No Report Available")

                    # -------------------------
                    # Delete Appointment
                    # -------------------------
                    if col3.button("Delete 🗑️", key=f"delete_approved_{appt[0]}"):
                        delete_appointment(appt[0])
                        st.warning("Appointment Deleted")
                        st.rerun()

        else:
            st.info("No matching approved appointments.")

    else:
        st.info("No approved appointments.")

