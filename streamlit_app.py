"""
Job Application Tracker Pro - Streamlit Web App
A beautiful, interactive web interface for tracking job applications
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json

# Import our modules
from job_tracker_manager import JobTrackerManager, generate_status_color_code
from ai_assistant import JobApplicationAI, generate_weekly_summary
from calendar_integration import CalendarIntegration

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        color: white;
        display: inline-block;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = JobTrackerManager()
    st.session_state.ai_assistant = JobApplicationAI()
    st.session_state.calendar = CalendarIntegration()

# Header
st.markdown('<h1 class="main-header">📊 Job Application Tracker Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Your AI-powered job search command center</p>', unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=Job+Tracker", use_container_width=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Application", "📝 Update Status", "📧 Generate Email", "💡 AI Suggestions", "📊 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📈 Quick Stats")

    analytics = st.session_state.tracker.get_analytics()
    st.metric("Total Apps", analytics.get('total_applications', 0))
    st.metric("Active", analytics.get('active_applications', 0))

    if analytics.get('total_applications', 0) > 0:
        st.metric("Interview Rate", f"{analytics['metrics'].get('interview_rate', 0)}%")

# Main content area
if page == "🏠 Dashboard":
    st.header("📊 Dashboard Overview")

    analytics = st.session_state.tracker.get_analytics()

    if analytics.get('total_applications', 0) == 0:
        st.info("👋 Welcome! Get started by adding your first job application using the '➕ Add Application' page.")
    else:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{analytics.get('total_applications', 0)}</h3>
                <p>Total Applications</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{analytics.get('active_applications', 0)}</h3>
                <p>Active Applications</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{analytics['metrics'].get('interview_rate', 0)}%</h3>
                <p>Interview Rate</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{analytics['metrics'].get('offer_rate', 0)}%</h3>
                <p>Offer Rate</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Status Breakdown")
            if analytics.get('status_breakdown'):
                status_data = pd.DataFrame([
                    {'Status': k, 'Count': v}
                    for k, v in analytics['status_breakdown'].items()
                ])

                # Create color map
                color_map = {
                    'Applied': '#FFB84D',
                    'Phone Screen': '#4DA6FF',
                    'Interview Scheduled': '#6B8EFF',
                    'Interviewed': '#9D7EFF',
                    'Second Interview': '#B066FF',
                    'Offer Received': '#66FF99',
                    'Accepted': '#00CC66',
                    'Rejected': '#FF6B6B',
                    'Withdrawn': '#999999',
                    'Follow-up Needed': '#FFD93D'
                }

                fig = px.bar(
                    status_data,
                    x='Count',
                    y='Status',
                    orientation='h',
                    color='Status',
                    color_discrete_map=color_map
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🎯 Success Metrics")
            metrics_data = pd.DataFrame([
                {'Metric': 'Interview Rate', 'Value': analytics['metrics'].get('interview_rate', 0)},
                {'Metric': 'Offer Rate', 'Value': analytics['metrics'].get('offer_rate', 0)},
                {'Metric': 'Acceptance Rate', 'Value': analytics['metrics'].get('acceptance_rate', 0)},
            ])

            fig = go.Figure(data=[
                go.Bar(
                    x=metrics_data['Metric'],
                    y=metrics_data['Value'],
                    marker_color=['#667eea', '#764ba2', '#9D7EFF']
                )
            ])
            fig.update_layout(
                yaxis_title="Percentage (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Action Items
        st.markdown("---")
        st.subheader("⚡ Action Items")

        action_items = st.session_state.tracker.get_applications_needing_action()

        if action_items['needs_followup']:
            st.warning(f"🔔 **{len(action_items['needs_followup'])} applications need follow-up**")
            for app in action_items['needs_followup']:
                st.markdown(f"- **{app['Company Name']}** - {app['Job Title']} (Follow-up: {app['Follow-up Date']})")

        if action_items['upcoming_interviews']:
            st.info(f"📅 **{len(action_items['upcoming_interviews'])} upcoming interviews**")
            for app in action_items['upcoming_interviews']:
                st.markdown(f"- **{app['Company Name']}** - {app['Job Title']} (Interview: {app['Interview Date']})")

        if action_items['stale_applications']:
            st.error(f"⏰ **{len(action_items['stale_applications'])} stale applications** (>14 days, no response)")
            for app in action_items['stale_applications']:
                st.markdown(f"- **{app['Company Name']}** - {app['Job Title']} ({app['Days Since Applied']} days)")

        # Recent Applications Table
        st.markdown("---")
        st.subheader("📋 Recent Applications")

        applications = st.session_state.tracker.load_applications()
        if applications:
            df = pd.DataFrame(applications)
            df = df[['Application ID', 'Company Name', 'Job Title', 'Application Date', 'Status', 'Days Since Applied', 'Success Score']]
            df = df.sort_values('Application Date', ascending=False).head(10)
            st.dataframe(df, use_container_width=True)

elif page == "➕ Add Application":
    st.header("➕ Add New Application")

    with st.form("add_application"):
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g., Google")
            job_title = st.text_input("Job Title *", placeholder="e.g., Software Engineer")
            application_date = st.date_input("Application Date *", value=datetime.now())
            status = st.selectbox("Status *", [
                "Applied", "Phone Screen", "Interview Scheduled", "Interviewed",
                "Second Interview", "Offer Received", "Accepted", "Rejected",
                "Withdrawn", "Follow-up Needed"
            ])
            contact_person = st.text_input("Contact Person", placeholder="e.g., Jane Smith")
            contact_email = st.text_input("Contact Email", placeholder="e.g., jane@company.com")

        with col2:
            salary_range = st.text_input("Salary Range", placeholder="e.g., $80k-$100k")
            job_url = st.text_input("Job URL", placeholder="https://...")
            interview_date = st.text_input("Interview Date", placeholder="YYYY-MM-DD HH:MM:SS (optional)")
            followup_date = st.date_input("Follow-up Date", value=None)
            notes = st.text_area("Notes", placeholder="Key requirements, interview notes, etc.")

        submitted = st.form_submit_button("➕ Add Application")

        if submitted:
            if not company_name or not job_title:
                st.error("⚠️ Company Name and Job Title are required!")
            else:
                app_data = {
                    'Company Name': company_name,
                    'Job Title': job_title,
                    'Application Date': application_date.strftime('%Y-%m-%d'),
                    'Status': status,
                    'Contact Person': contact_person,
                    'Contact Email': contact_email,
                    'Salary Range': salary_range,
                    'Job URL': job_url,
                    'Interview Date': interview_date,
                    'Follow-up Date': followup_date.strftime('%Y-%m-%d') if followup_date else '',
                    'Notes': notes
                }

                application = st.session_state.tracker.add_application(app_data)

                st.success(f"✅ Application added successfully!")
                st.info(f"""
                **Application Details:**
                - 📝 Application ID: {application['Application ID']}
                - 🏢 Company: {application['Company Name']}
                - 💼 Role: {application['Job Title']}
                - 📅 Applied: {application['Application Date']}
                - ⏱️ Days since applied: {application['Days Since Applied']}
                - 🎯 Success Score: {application['Success Score']}/100
                """)

                # Get AI suggestions
                all_apps = st.session_state.tracker.load_applications()
                suggestions = st.session_state.ai_assistant.get_application_suggestions(application, all_apps)

                if suggestions['immediate_actions']:
                    st.warning("**💡 Immediate Actions:**")
                    for action in suggestions['immediate_actions']:
                        st.markdown(f"- {action}")

elif page == "📝 Update Status":
    st.header("📝 Update Application Status")

    applications = st.session_state.tracker.load_applications()

    if not applications:
        st.info("No applications to update. Add your first application!")
    else:
        # Create dropdown of applications
        app_options = [f"{app['Company Name']} - {app['Job Title']}" for app in applications]
        selected_app = st.selectbox("Select Application", app_options)

        if selected_app:
            # Find the application
            company, job_title = selected_app.split(" - ", 1)
            target_app = next((app for app in applications if app['Company Name'] == company and app['Job Title'] == job_title), None)

            if target_app:
                st.subheader(f"Current Status: {target_app['Status']}")

                with st.form("update_status"):
                    new_status = st.selectbox("New Status", [
                        "Applied", "Phone Screen", "Interview Scheduled", "Interviewed",
                        "Second Interview", "Offer Received", "Accepted", "Rejected",
                        "Withdrawn", "Follow-up Needed"
                    ], index=0)

                    interview_date = st.text_input("Interview Date", value=target_app.get('Interview Date', ''), placeholder="YYYY-MM-DD HH:MM:SS")
                    followup_date = st.date_input("Follow-up Date", value=None)
                    notes = st.text_area("Notes", value=target_app.get('Notes', ''))

                    submitted = st.form_submit_button("💾 Update Status")

                    if submitted:
                        updates = {
                            'Status': new_status,
                            'Interview Date': interview_date,
                            'Follow-up Date': followup_date.strftime('%Y-%m-%d') if followup_date else target_app.get('Follow-up Date', ''),
                            'Notes': notes
                        }

                        updated_app = st.session_state.tracker.update_application(target_app['Application ID'], updates)

                        st.success(f"✅ Updated {company} - {job_title}")
                        st.info(f"""
                        **Updated Details:**
                        - Status: {updated_app['Status']}
                        - Days Since Applied: {updated_app['Days Since Applied']}
                        - Success Score: {updated_app['Success Score']}/100
                        """)

elif page == "📧 Generate Email":
    st.header("📧 Generate Follow-up Email")

    applications = st.session_state.tracker.load_applications()

    if not applications:
        st.info("No applications yet. Add applications first!")
    else:
        app_options = [f"{app['Company Name']} - {app['Job Title']}" for app in applications]
        selected_app = st.selectbox("Select Application", app_options)

        if selected_app and st.button("✨ Generate Email"):
            company, job_title = selected_app.split(" - ", 1)
            target_app = next((app for app in applications if app['Company Name'] == company and app['Job Title'] == job_title), None)

            if target_app:
                email = st.session_state.ai_assistant.generate_followup_email(target_app)

                st.success("📧 Follow-up email generated!")

                st.subheader("Subject:")
                st.code(email['subject'])

                st.subheader("Body:")
                st.text_area("Email Body", email['body'], height=400)

                st.subheader("💡 Customization Tips:")
                for tip in email['tips']:
                    st.markdown(f"- {tip}")

                # Show interview prep if applicable
                if target_app['Status'] in ['Interview Scheduled', 'Phone Screen']:
                    st.markdown("---")
                    st.subheader("📚 Interview Preparation Checklist")
                    prep = st.session_state.ai_assistant.generate_interview_prep_checklist(target_app)
                    for item in prep:
                        st.markdown(item)

elif page == "💡 AI Suggestions":
    st.header("💡 AI Suggestions & Insights")

    applications = st.session_state.tracker.load_applications()

    if not applications:
        st.info("Add applications to get personalized suggestions!")
    else:
        tab1, tab2 = st.tabs(["Overall Strategy", "Specific Application"])

        with tab1:
            st.subheader("📊 Overall Job Search Strategy")

            analytics = st.session_state.tracker.get_analytics()

            st.metric("Total Applications", analytics.get('total_applications', 0))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Interview Rate", f"{analytics['metrics'].get('interview_rate', 0)}%")
            with col2:
                st.metric("Offer Rate", f"{analytics['metrics'].get('offer_rate', 0)}%")
            with col3:
                st.metric("Avg Days", analytics.get('average_days_since_applied', 0))

            st.markdown("---")

            # General tips
            st.subheader("🎯 Strategy Recommendations")

            interview_rate = analytics['metrics'].get('interview_rate', 0)
            if interview_rate < 10:
                st.warning("📊 Your interview rate is below 10%. Consider: improving your resume, tailoring applications more, or targeting better-fit roles.")
            elif interview_rate > 20:
                st.success("🎉 Great interview rate! Focus on interview preparation to convert more to offers.")

            st.markdown("**General Best Practices:**")
            st.markdown("- 🎯 Quality over quantity: Tailor each application to the role")
            st.markdown("- 🔗 Network actively: 70% of jobs are filled through networking")
            st.markdown("- 📧 Follow up strategically: Wait 7-10 days, then send a polite email")
            st.markdown("- 💼 Optimize your LinkedIn: Recruiters search there daily")
            st.markdown("- 📚 Keep learning: Add new skills relevant to your target roles")

        with tab2:
            st.subheader("🔍 Specific Application Analysis")

            app_options = [f"{app['Company Name']} - {app['Job Title']}" for app in applications]
            selected_app = st.selectbox("Select Application", app_options, key="suggestions_select")

            if selected_app and st.button("🔮 Get AI Suggestions"):
                company, job_title = selected_app.split(" - ", 1)
                target_app = next((app for app in applications if app['Company Name'] == company and app['Job Title'] == job_title), None)

                if target_app:
                    suggestions = st.session_state.ai_assistant.get_application_suggestions(target_app, applications)

                    if suggestions['immediate_actions']:
                        st.subheader("⚡ Immediate Actions")
                        for action in suggestions['immediate_actions']:
                            st.info(action)

                    if suggestions['warnings']:
                        st.subheader("⚠️ Warnings")
                        for warning in suggestions['warnings']:
                            st.warning(warning)

                    if suggestions['optimizations']:
                        st.subheader("💡 Optimizations")
                        for opt in suggestions['optimizations']:
                            st.success(opt)

elif page == "📊 Analytics":
    st.header("📊 Detailed Analytics")

    applications = st.session_state.tracker.load_applications()

    if not applications:
        st.info("Add applications to see analytics!")
    else:
        df = pd.DataFrame(applications)

        # Export option
        if st.button("📥 Export to CSV"):
            filename = st.session_state.tracker.export_to_csv()
            st.success(f"✅ Data exported to: {filename}")

            with open(filename, 'rb') as f:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=f,
                    file_name=filename,
                    mime='text/csv'
                )

        st.markdown("---")

        # Timeline chart
        st.subheader("📈 Application Timeline")
        df_timeline = df.copy()
        df_timeline['Application Date'] = pd.to_datetime(df_timeline['Application Date'])
        df_timeline = df_timeline.sort_values('Application Date')

        fig = px.scatter(
            df_timeline,
            x='Application Date',
            y='Company Name',
            color='Status',
            size='Success Score',
            hover_data=['Job Title', 'Days Since Applied']
        )
        st.plotly_chart(fig, use_container_width=True)

        # Company breakdown
        st.subheader("🏢 Top Companies by Success Score")
        companies_scores = df.groupby('Company Name')['Success Score'].mean().sort_values(ascending=False).head(10)

        fig = px.bar(
            x=companies_scores.values,
            y=companies_scores.index,
            orientation='h',
            labels={'x': 'Average Success Score', 'y': 'Company'}
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")

    st.subheader("📊 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export All Data"):
            filename = st.session_state.tracker.export_to_csv()
            st.success(f"✅ Exported to: {filename}")

    with col2:
        uploaded_file = st.file_uploader("📤 Import CSV", type=['csv'])
        if uploaded_file is not None:
            st.info("Import functionality - CSV file uploaded!")

    st.markdown("---")

    st.subheader("🔔 Calendar Integration")
    st.info("📅 Google Calendar integration is available. Connect your calendar to auto-create interview reminders.")

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.markdown("""
    **Job Application Tracker Pro** v1.0

    Built with ❤️ using:
    - Streamlit for the web interface
    - Python for data management
    - AI for smart suggestions
    - Google Calendar API for reminders

    **Features:**
    - ✅ Track unlimited job applications
    - ✅ AI-powered follow-up emails
    - ✅ Visual analytics dashboard
    - ✅ Smart success scoring
    - ✅ Calendar integration
    - ✅ Personalized suggestions

    **AgentApp ID:** 33SgDCUd1M
    """)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999;">Built with ❤️ on CREAO Platform | Job Application Tracker Pro</p>',
    unsafe_allow_html=True
)
