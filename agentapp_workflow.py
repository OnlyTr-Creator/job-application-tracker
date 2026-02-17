"""
Main AgentApp Workflow for Job Application Tracker
Orchestrates all features: tracking, AI assistance, analytics, reminders
"""

import os
import json
from datetime import datetime
from job_tracker_manager import JobTrackerManager, generate_status_color_code
from ai_assistant import JobApplicationAI, generate_weekly_summary


class JobTrackerWorkflow:
    """Main workflow orchestrator for the Job Application Tracker AgentApp"""

    def __init__(self):
        self.tracker = JobTrackerManager()
        self.ai_assistant = JobApplicationAI()

    def process_form_submission(self, form_data: dict) -> dict:
        """
        Process the form submission and route to appropriate action

        Args:
            form_data: Dictionary containing all form fields from user input

        Returns:
            Dictionary with results and next steps
        """
        action = form_data.get('Action', 'add')

        if action == 'add':
            return self.add_new_application(form_data)
        elif action == 'update':
            return self.update_application_status(form_data)
        elif action == 'dashboard':
            return self.generate_dashboard()
        elif action == 'followup':
            return self.generate_followup_email(form_data)
        elif action == 'suggestions':
            return self.get_ai_suggestions(form_data)
        elif action == 'export':
            return self.export_data()
        else:
            return {'error': 'Unknown action'}

    def add_new_application(self, form_data: dict) -> dict:
        """Add a new job application to the tracker"""

        # Extract application data
        app_data = {
            'Company Name': form_data.get('Company Name', ''),
            'Job Title': form_data.get('Job Title', ''),
            'Application Date': form_data.get('Application Date', ''),
            'Status': form_data.get('Status', 'Applied'),
            'Contact Person': form_data.get('Contact Person', ''),
            'Contact Email': form_data.get('Contact Email', ''),
            'Salary Range': form_data.get('Salary Range', ''),
            'Job URL': form_data.get('Job URL', ''),
            'Interview Date': form_data.get('Interview Date', ''),
            'Follow-up Date': form_data.get('Follow-up Date', ''),
            'Notes': form_data.get('Notes', '')
        }

        # Add to tracker
        application = self.tracker.add_application(app_data)

        # Generate automatic follow-up date if not provided
        if not app_data.get('Follow-up Date'):
            from datetime import timedelta
            app_date = datetime.strptime(app_data['Application Date'], '%Y-%m-%d')
            suggested_followup = app_date + timedelta(days=7)
            application['Suggested Follow-up Date'] = suggested_followup.strftime('%Y-%m-%d')

        # Get AI suggestions for this application
        all_apps = self.tracker.load_applications()
        suggestions = self.ai_assistant.get_application_suggestions(application, all_apps)

        return {
            'status': 'success',
            'message': f'✅ Application added successfully!',
            'application': application,
            'suggestions': suggestions,
            'next_steps': [
                f'📝 Application ID: {application["Application ID"]}',
                f'🏢 Company: {application["Company Name"]}',
                f'💼 Role: {application["Job Title"]}',
                f'📅 Applied: {application["Application Date"]}',
                f'⏱️ Days since applied: {application["Days Since Applied"]}',
                f'🎯 Success Score: {application["Success Score"]}/100'
            ],
            'color_code': generate_status_color_code(application['Status'])
        }

    def update_application_status(self, form_data: dict) -> dict:
        """Update an existing application's status"""

        # In a real implementation, you'd have an app_id field
        # For now, we'll match by company + job title
        company = form_data.get('Company Name', '')
        job_title = form_data.get('Job Title', '')

        applications = self.tracker.load_applications()
        target_app = None

        for app in applications:
            if app['Company Name'] == company and app['Job Title'] == job_title:
                target_app = app
                break

        if not target_app:
            return {
                'status': 'error',
                'message': f'Could not find application for {job_title} at {company}'
            }

        # Update the application
        updates = {
            'Status': form_data.get('Status'),
            'Interview Date': form_data.get('Interview Date', target_app.get('Interview Date', '')),
            'Follow-up Date': form_data.get('Follow-up Date', target_app.get('Follow-up Date', '')),
            'Notes': form_data.get('Notes', target_app.get('Notes', ''))
        }

        updated_app = self.tracker.update_application(target_app['Application ID'], updates)

        # Check if we need to trigger any automations
        automations = self.check_automations(updated_app)

        return {
            'status': 'success',
            'message': f'✅ Updated {company} - {job_title}',
            'application': updated_app,
            'automations': automations,
            'color_code': generate_status_color_code(updated_app['Status'])
        }

    def generate_dashboard(self) -> dict:
        """Generate analytics dashboard"""

        analytics = self.tracker.get_analytics()
        action_items = self.tracker.get_applications_needing_action()

        # Prepare dashboard data
        dashboard_data = {
            'analytics': analytics,
            'action_items': {
                'followups': action_items.get('needs_followup', []),
                'interviews': action_items.get('upcoming_interviews', []),
                'stale': action_items.get('stale_applications', [])
            },
            'html_file': 'dashboard_template.html'
        }

        # Format action items for display
        formatted_actions = []

        for app in action_items.get('needs_followup', []):
            formatted_actions.append({
                'title': f'🔔 Follow up with {app["Company Name"]}',
                'description': f'{app["Job Title"]} - Follow-up date: {app["Follow-up Date"]}',
                'urgent': True
            })

        for app in action_items.get('upcoming_interviews', []):
            formatted_actions.append({
                'title': f'📅 Upcoming interview at {app["Company Name"]}',
                'description': f'{app["Job Title"]} - Interview: {app["Interview Date"]}',
                'urgent': False
            })

        for app in action_items.get('stale_applications', []):
            formatted_actions.append({
                'title': f'⏰ Check status of {app["Company Name"]} application',
                'description': f'{app["Job Title"]} - {app["Days Since Applied"]} days with no response',
                'urgent': False
            })

        return {
            'status': 'success',
            'message': '📊 Dashboard generated successfully',
            'analytics': analytics,
            'action_items': formatted_actions,
            'visualization': 'See dashboard_template.html for visual analytics'
        }

    def generate_followup_email(self, form_data: dict) -> dict:
        """Generate AI-powered follow-up email"""

        company = form_data.get('Company Name', '')
        job_title = form_data.get('Job Title', '')

        applications = self.tracker.load_applications()
        target_app = None

        for app in applications:
            if app['Company Name'] == company and app['Job Title'] == job_title:
                target_app = app
                break

        if not target_app:
            return {
                'status': 'error',
                'message': f'Could not find application for {job_title} at {company}'
            }

        # Generate follow-up email
        email = self.ai_assistant.generate_followup_email(target_app)

        # Generate interview prep if applicable
        prep_checklist = []
        if target_app['Status'] in ['Interview Scheduled', 'Phone Screen']:
            prep_checklist = self.ai_assistant.generate_interview_prep_checklist(target_app)

        return {
            'status': 'success',
            'message': '📧 Follow-up email generated',
            'email': email,
            'prep_checklist': prep_checklist
        }

    def get_ai_suggestions(self, form_data: dict) -> dict:
        """Get AI-powered suggestions for improving job search"""

        company = form_data.get('Company Name', '')
        job_title = form_data.get('Job Title', '')

        applications = self.tracker.load_applications()

        # If specific application provided, get suggestions for it
        if company and job_title:
            target_app = None
            for app in applications:
                if app['Company Name'] == company and app['Job Title'] == job_title:
                    target_app = app
                    break

            if target_app:
                suggestions = self.ai_assistant.get_application_suggestions(target_app, applications)

                # Also get interview notes summary if available
                notes_summary = None
                if target_app.get('Notes'):
                    notes_summary = self.ai_assistant.summarize_interview_notes(
                        target_app['Notes'],
                        target_app['Job Title'],
                        target_app['Company Name']
                    )

                return {
                    'status': 'success',
                    'message': '💡 AI suggestions generated',
                    'suggestions': suggestions,
                    'notes_summary': notes_summary
                }

        # Otherwise, provide general job search strategy
        analytics = self.tracker.get_analytics()

        general_tips = {
            'strategy': [
                '🎯 Quality over quantity: Tailor each application to the role',
                '🔗 Network actively: 70% of jobs are filled through networking',
                '📧 Follow up strategically: Wait 7-10 days, then send a polite email',
                '💼 Optimize your LinkedIn: Recruiters search there daily',
                '📚 Keep learning: Add new skills relevant to your target roles'
            ],
            'based_on_data': []
        }

        # Add data-driven insights
        if analytics.get('total_applications', 0) > 0:
            interview_rate = analytics['metrics'].get('interview_rate', 0)
            if interview_rate < 10:
                general_tips['based_on_data'].append(
                    '📊 Your interview rate is below average. Consider: improving resume, tailoring applications, or targeting better-fit roles.'
                )
            elif interview_rate > 20:
                general_tips['based_on_data'].append(
                    '🎉 Great interview rate! Focus on interview preparation to convert more to offers.'
                )

        return {
            'status': 'success',
            'message': '💡 General job search suggestions',
            'suggestions': general_tips,
            'analytics_summary': analytics
        }

    def export_data(self) -> dict:
        """Export all application data"""

        filename = self.tracker.export_to_csv()
        applications = self.tracker.load_applications()
        analytics = self.tracker.get_analytics()

        return {
            'status': 'success',
            'message': f'✅ Data exported successfully',
            'filename': filename,
            'total_applications': len(applications),
            'analytics_snapshot': analytics
        }

    def check_automations(self, application: dict) -> list:
        """Check what automations should trigger based on application state"""

        automations = []
        status = application.get('Status')

        # Trigger based on status changes
        if status == 'Interview Scheduled':
            automations.append({
                'type': 'calendar_reminder',
                'message': f'📅 Set calendar reminder for interview at {application["Company Name"]}',
                'data': {
                    'title': f'Interview: {application["Job Title"]} at {application["Company Name"]}',
                    'date': application.get('Interview Date'),
                    'description': application.get('Notes', '')
                }
            })

            automations.append({
                'type': 'prep_checklist',
                'message': '📚 Review interview preparation checklist',
                'checklist': self.ai_assistant.generate_interview_prep_checklist(application)
            })

        if status in ['Interviewed', 'Phone Screen']:
            automations.append({
                'type': 'followup_reminder',
                'message': '📧 Send thank-you email within 24 hours',
                'email_template': self.ai_assistant.generate_followup_email(application)
            })

        if status == 'Offer Received':
            automations.append({
                'type': 'celebration',
                'message': '🎉 Congratulations on the offer! Review compensation and benefits carefully.'
            })

        return automations


def main():
    """Main entry point for testing"""
    workflow = JobTrackerWorkflow()

    # Example: Add a test application
    test_data = {
        'Action': 'add',
        'Company Name': 'TechCorp',
        'Job Title': 'Software Engineer',
        'Application Date': '2026-02-10',
        'Status': 'Applied',
        'Contact Person': 'Jane Smith',
        'Contact Email': 'jane.smith@techcorp.com',
        'Salary Range': '$100k-$130k',
        'Job URL': 'https://techcorp.com/careers/swe',
        'Notes': 'Exciting role working on AI products'
    }

    result = workflow.process_form_submission(test_data)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
