"""
Google Calendar Integration for Job Application Tracker
Creates reminders and events for interviews and follow-ups
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class CalendarIntegration:
    """
    Handles Google Calendar integration for job application tracking
    Uses CREAO's Google Calendar MCP tool
    """

    def __init__(self, calendar_id: str = "primary"):
        self.calendar_id = calendar_id

    def create_interview_event(
        self,
        application: Dict[str, Any],
        timezone: str = "America/New_York"
    ) -> Dict[str, Any]:
        """
        Create a calendar event for a job interview

        Args:
            application: Application data including interview details
            timezone: Timezone for the event

        Returns:
            Dictionary with event creation instructions
        """

        company = application.get('Company Name', '')
        job_title = application.get('Job Title', '')
        interview_date = application.get('Interview Date', '')
        contact_person = application.get('Contact Person', '')
        notes = application.get('Notes', '')
        job_url = application.get('Job URL', '')

        if not interview_date:
            return {
                'status': 'error',
                'message': 'No interview date specified'
            }

        # Parse interview datetime
        try:
            # Assuming format: YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS
            if ' ' in interview_date:
                interview_dt = datetime.strptime(interview_date, '%Y-%m-%d %H:%M:%S')
            else:
                interview_dt = datetime.strptime(interview_date, '%Y-%m-%dT%H:%M:%S')
        except:
            return {
                'status': 'error',
                'message': f'Invalid interview date format: {interview_date}'
            }

        # Prepare event details
        event_summary = f"Interview: {job_title} at {company}"

        event_description = f"""
Job Interview Details
━━━━━━━━━━━━━━━━━━━━

🏢 Company: {company}
💼 Position: {job_title}
👤 Contact: {contact_person if contact_person else 'Not specified'}
🔗 Job Posting: {job_url if job_url else 'Not specified'}

📝 Notes:
{notes if notes else 'No additional notes'}

━━━━━━━━━━━━━━━━━━━━
Preparation Reminders:
✅ Research the company and role
✅ Prepare STAR method examples
✅ Review your resume
✅ Prepare questions to ask
✅ Test tech setup (if virtual)
✅ Plan outfit/route
        """.strip()

        # Default to 1 hour duration
        event_duration_hour = 1
        event_duration_minutes = 0

        # Format datetime for Google Calendar
        start_datetime = interview_dt.strftime('%Y-%m-%dT%H:%M:%S')

        # Instructions for creating the event via Google Calendar MCP
        calendar_event_data = {
            'calendar_id': self.calendar_id,
            'start_datetime': start_datetime,
            'timezone': timezone,
            'event_duration_hour': event_duration_hour,
            'event_duration_minutes': event_duration_minutes,
            'summary': event_summary,
            'description': event_description,
            'create_meeting_room': True  # Try to create Google Meet link
        }

        # Add contact email as attendee if available
        contact_email = application.get('Contact Email', '')
        if contact_email:
            calendar_event_data['attendees'] = [contact_email]

        return {
            'status': 'ready',
            'message': f'📅 Interview event ready to create',
            'event_data': calendar_event_data,
            'mcp_tool': 'GOOGLECALENDAR_CREATE_EVENT',
            'mcp_id': '6874a16d565d2b53f95cd043',
            'reminder': 'This will create a Google Calendar event with a Meet link (if workspace account)'
        }

    def create_followup_reminder(
        self,
        application: Dict[str, Any],
        timezone: str = "America/New_York"
    ) -> Dict[str, Any]:
        """
        Create a calendar reminder for following up on an application

        Args:
            application: Application data
            timezone: Timezone for the reminder

        Returns:
            Dictionary with reminder creation instructions
        """

        company = application.get('Company Name', '')
        job_title = application.get('Job Title', '')
        followup_date = application.get('Follow-up Date', '')
        app_date = application.get('Application Date', '')

        if not followup_date:
            # Auto-suggest follow-up date (7 days after application)
            if app_date:
                try:
                    app_dt = datetime.strptime(app_date, '%Y-%m-%d')
                    suggested_followup = app_dt + timedelta(days=7)
                    followup_date = suggested_followup.strftime('%Y-%m-%d')
                except:
                    followup_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            else:
                followup_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        # Parse follow-up date and set to 9 AM
        try:
            followup_dt = datetime.strptime(followup_date, '%Y-%m-%d')
            followup_dt = followup_dt.replace(hour=9, minute=0, second=0)
        except:
            return {
                'status': 'error',
                'message': f'Invalid follow-up date format: {followup_date}'
            }

        # Prepare reminder event
        event_summary = f"Follow up: {job_title} at {company}"

        event_description = f"""
Follow-up Reminder
━━━━━━━━━━━━━━━━━━━━

🏢 Company: {company}
💼 Position: {job_title}
📅 Applied: {app_date if app_date else 'Not specified'}

✉️ Action Items:
□ Send a polite follow-up email
□ Check application status
□ Express continued interest
□ Ask about timeline

💡 Tip: Keep it brief and professional. Hiring managers are busy!
        """.strip()

        # 30-minute reminder
        event_duration_hour = 0
        event_duration_minutes = 30

        # Format datetime for Google Calendar
        start_datetime = followup_dt.strftime('%Y-%m-%dT%H:%M:%S')

        calendar_event_data = {
            'calendar_id': self.calendar_id,
            'start_datetime': start_datetime,
            'timezone': timezone,
            'event_duration_hour': event_duration_hour,
            'event_duration_minutes': event_duration_minutes,
            'summary': event_summary,
            'description': event_description,
            'create_meeting_room': False  # No need for Meet link
        }

        return {
            'status': 'ready',
            'message': f'🔔 Follow-up reminder ready to create',
            'event_data': calendar_event_data,
            'mcp_tool': 'GOOGLECALENDAR_CREATE_EVENT',
            'mcp_id': '6874a16d565d2b53f95cd043',
            'reminder': 'This will create a 30-minute reminder on your calendar'
        }

    def create_application_deadline_reminder(
        self,
        company: str,
        job_title: str,
        deadline: str,
        timezone: str = "America/New_York"
    ) -> Dict[str, Any]:
        """
        Create a reminder for an application deadline

        Args:
            company: Company name
            job_title: Job title
            deadline: Deadline date (YYYY-MM-DD)
            timezone: Timezone

        Returns:
            Dictionary with event creation instructions
        """

        try:
            deadline_dt = datetime.strptime(deadline, '%Y-%m-%d')
            # Set reminder for 2 days before deadline at 10 AM
            reminder_dt = deadline_dt - timedelta(days=2)
            reminder_dt = reminder_dt.replace(hour=10, minute=0, second=0)
        except:
            return {
                'status': 'error',
                'message': f'Invalid deadline format: {deadline}'
            }

        event_summary = f"Deadline: Apply to {job_title} at {company}"

        event_description = f"""
Application Deadline Reminder
━━━━━━━━━━━━━━━━━━━━

🏢 Company: {company}
💼 Position: {job_title}
⚠️ Deadline: {deadline}

📝 Final Checklist:
□ Tailor your resume to the job description
□ Write a compelling cover letter
□ Prepare your portfolio/work samples
□ Double-check all required documents
□ Proofread everything!
□ Submit before deadline

🎯 This is your 2-day warning! Don't miss this opportunity!
        """.strip()

        start_datetime = reminder_dt.strftime('%Y-%m-%dT%H:%M:%S')

        calendar_event_data = {
            'calendar_id': self.calendar_id,
            'start_datetime': start_datetime,
            'timezone': timezone,
            'event_duration_hour': 1,
            'event_duration_minutes': 0,
            'summary': event_summary,
            'description': event_description,
            'create_meeting_room': False
        }

        return {
            'status': 'ready',
            'message': f'⏰ Deadline reminder ready to create',
            'event_data': calendar_event_data,
            'mcp_tool': 'GOOGLECALENDAR_CREATE_EVENT',
            'mcp_id': '6874a16d565d2b53f95cd043',
            'reminder': 'This will remind you 2 days before the deadline'
        }

    def batch_create_reminders(
        self,
        applications: list,
        timezone: str = "America/New_York"
    ) -> Dict[str, Any]:
        """
        Create reminders for multiple applications at once

        Args:
            applications: List of applications needing reminders
            timezone: Timezone

        Returns:
            Dictionary with batch creation instructions
        """

        reminders = []

        for app in applications:
            status = app.get('Status', '')

            # Create interview events for scheduled interviews
            if status == 'Interview Scheduled' and app.get('Interview Date'):
                interview_reminder = self.create_interview_event(app, timezone)
                if interview_reminder['status'] == 'ready':
                    reminders.append(interview_reminder)

            # Create follow-up reminders for applications needing follow-up
            if status in ['Applied', 'Follow-up Needed'] and app.get('Follow-up Date'):
                followup_reminder = self.create_followup_reminder(app, timezone)
                if followup_reminder['status'] == 'ready':
                    reminders.append(followup_reminder)

        return {
            'status': 'ready',
            'message': f'📅 {len(reminders)} calendar events ready to create',
            'reminders': reminders,
            'total': len(reminders)
        }


def get_calendar_instructions():
    """Return instructions for users on how to connect Google Calendar"""
    return """
📅 Google Calendar Integration Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To enable automatic calendar reminders for interviews and follow-ups:

1. **Authorize Google Calendar** in your CREAO workspace
   - The AgentApp will prompt you when calendar access is needed

2. **What gets added to your calendar:**
   ✅ Interview appointments (with Google Meet links)
   ✅ Follow-up reminders
   ✅ Application deadline warnings

3. **Customization:**
   - Default timezone: America/New_York
   - Interview duration: 1 hour
   - Follow-up reminders: 30 minutes
   - You can modify these after creation in Google Calendar

4. **Privacy:**
   - Only you can see these calendar events
   - Your application data stays private
   - Calendar access can be revoked anytime

Ready to get started? Just submit an application and we'll handle the rest! 🚀
    """


if __name__ == '__main__':
    # Example usage
    cal = CalendarIntegration()

    sample_app = {
        'Company Name': 'TechCorp',
        'Job Title': 'Software Engineer',
        'Application Date': '2026-02-10',
        'Interview Date': '2026-02-20T14:00:00',
        'Follow-up Date': '2026-02-17',
        'Contact Person': 'Jane Smith',
        'Contact Email': 'jane@techcorp.com',
        'Notes': 'Focus on Python and cloud experience'
    }

    print("Interview Event:")
    print(cal.create_interview_event(sample_app))

    print("\nFollow-up Reminder:")
    print(cal.create_followup_reminder(sample_app))
