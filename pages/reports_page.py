import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
from database import get_reports

# Page Configuration
st.set_page_config(page_title="Patient Reports Archive", page_icon="📄", layout="wide")

st.title("📄 Patient Diagnostic Archive")
st.markdown("Review and manage all AI-generated retinal diagnostic reports.")

# Fetch data from Database
reports = get_reports() 

if reports:
    # -----------------------------
    # 1. Data Processing & Analytics
    # -----------------------------
    # Expected columns from DB: (ID, Name, Result, Confidence, Path, Date)
    df = pd.DataFrame(reports, columns=["ID", "Patient", "Result", "Confidence", "Path", "Date"])
    
    # FIX: Ensure Confidence is numeric for calculations
    df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce')

    # Header Metrics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Reports", len(df))
    
    with col_stat2:
        high_priority = len(df[df['Result'].isin(['Severe', 'Proliferative'])])
        st.metric("High Priority Cases", high_priority, delta=f"{high_priority} Urgent", delta_color="inverse")
    
    with col_stat3:
        avg_conf = df['Confidence'].mean()
        display_conf = f"{avg_conf:.1f}%" if not np.isnan(avg_conf) else "0.0%"
        st.metric("Avg. AI Confidence", display_conf)

    st.markdown("---")

    # -----------------------------
    # 2. Visual Analytics
    # -----------------------------
    with st.container():
        chart_col, info_col = st.columns([2, 1])
        
        with chart_col:
            # Distribution Chart
            fig = px.pie(df, names='Result', title='Overall Severity Distribution',
                         color_discrete_sequence=px.colors.sequential.RdBu_r,
                         hole=0.4)
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        with info_col:
            st.markdown("### Quick Filter Guide")
            st.write("🔴 **Severe/Proliferative:** Immediate Action")
            st.write("🟡 **Mild/Moderate:** Follow-up Required")
            st.write("🟢 **No DR:** Routine Checkup")

    # -----------------------------
    # 3. Search and Filter
    # -----------------------------
    st.subheader("🔍 Search Database")
    search_query = st.text_input("Enter Patient Name", "").lower()
    
    filtered_df = df[df['Patient'].str.lower().str.contains(search_query)]

    # -----------------------------
    # 4. Interactive Report List
    # -----------------------------
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            severity = row['Result']
            # Assign color indicators
            if severity in ["Severe", "Proliferative"]:
                status_color = "🔴"
            elif severity in ["Mild", "Moderate"]:
                status_color = "🟡"
            else:
                status_color = "🟢"
            
            with st.expander(f"{status_color} {row['Patient']} | Result: {severity} | Date: {row['Date']}"):
                c1, c2, c3 = st.columns([2, 1, 1])
                
                with c1:
                    st.write(f"**Patient Name:** {row['Patient']}")
                    st.write(f"**AI Diagnosis:** `{severity}`")
                    st.write(f"**Diagnostic Date:** {row['Date']}")
                
                with c2:
                    st.write("**AI Confidence Score**")
                    conf_val = row['Confidence'] if not np.isnan(row['Confidence']) else 0.0
                    st.progress(float(conf_val)/100)
                    st.write(f"{conf_val:.2f}%")

                with c3:
                    st.write("**Report Management**")
                    if row['Path'] and os.path.exists(row['Path']):
                        with open(row['Path'], "rb") as f:
                            st.download_button(
                                label="Download PDF 📄",
                                data=f,
                                file_name=os.path.basename(row['Path']),
                                key=f"dl_{row['ID']}"
                            )
                    else:
                        st.error("PDF File Missing")
    else:
        st.warning("No records found matching that name.")

else:
    st.info("The database is currently empty. Start analyzing images to generate reports!")

# Sidebar Severity Help
st.sidebar.title("System Legend")
st.sidebar.markdown("""
**Diagnostic Classification:**
- **Stage 0:** No DR
- **Stage 1:** Mild NPDR
- **Stage 2:** Moderate NPDR
- **Stage 3:** Severe NPDR
- **Stage 4:** Proliferative DR
""")