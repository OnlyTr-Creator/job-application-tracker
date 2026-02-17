"""
Job Application Tracker Manager
Handles data management, calculations, and analytics for job applications
"""

import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class JobTrackerManager:
    def __init__(self, csv_file='job_applications.csv'):
        self.csv_file = csv_file
        self.headers = [
            'Application ID', 'Company Name', 'Job Title', 'Application Date',
            'Status', 'Days Since Applied', 'Contact Person', 'Contact Email',
            'Salary Range', 'Job URL', 'Interview Date', 'Follow-up Date',
            'Notes', 'Last Updated', 'Success Score'
        ]
        self.initialize_csv()

    def initialize_csv(self):
        """Create CSV file if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def generate_app_id(self) -> str:
        """Generate unique application ID"""
        applications = self.load_applications()
        if not applications:
            return 'APP001'

        # Extract numbers from existing IDs and get max
        ids = [int(app['Application ID'].replace('APP', '')) for app in applications if app['Application ID'].startswith('APP')]
        next_id = max(ids) + 1 if ids else 1
        return f'APP{next_id:03d}'

    def calculate_days_since_applied(self, application_date: str) -> int:
        """Calculate days since application date"""
        try:
            app_date = datetime.strptime(application_date, '%Y-%m-%d')
            today = datetime.now()
            delta = today - app_date
            return delta.days
        except:
            return 0

    def calculate_success_score(self, status: str, days: int) -> int:
        """Calculate success probability score (0-100)"""
        status_weights = {
            'Applied': 30,
            'Phone Screen': 50,
            'Interview Scheduled': 60,
            'Interviewed': 70,
            'Second Interview': 85,
            'Offer Received': 95,
            'Accepted': 100,
            'Rejected': 0,
            'Withdrawn': 0,
            'Follow-up Needed': 40
        }

        base_score = status_weights.get(status, 30)

        # Reduce score if too much time has passed without progress
        if status in ['Applied', 'Follow-up Needed'] and days > 14:
            base_score = max(10, base_score - (days - 14) * 2)

        return min(100, max(0, base_score))

    def add_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new job application"""
        app_id = self.generate_app_id()

        # Calculate automatic fields
        days_since = self.calculate_days_since_applied(data['Application Date'])
        success_score = self.calculate_success_score(data['Status'], days_since)

        application = {
            'Application ID': app_id,
            'Company Name': data.get('Company Name', ''),
            'Job Title': data.get('Job Title', ''),
            'Application Date': data.get('Application Date', ''),
            'Status': data.get('Status', 'Applied'),
            'Days Since Applied': days_since,
            'Contact Person': data.get('Contact Person', ''),
            'Contact Email': data.get('Contact Email', ''),
            'Salary Range': data.get('Salary Range', ''),
            'Job URL': data.get('Job URL', ''),
            'Interview Date': data.get('Interview Date', ''),
            'Follow-up Date': data.get('Follow-up Date', ''),
            'Notes': data.get('Notes', ''),
            'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Success Score': success_score
        }

        # Write to CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(application)

        return application

    def load_applications(self) -> List[Dict[str, Any]]:
        """Load all applications from CSV"""
        applications = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                applications = list(reader)
        return applications

    def update_application(self, app_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing application"""
        applications = self.load_applications()
        updated_app = None

        for app in applications:
            if app['Application ID'] == app_id:
                # Update fields
                for key, value in updates.items():
                    if key in self.headers:
                        app[key] = value

                # Recalculate automatic fields
                app['Days Since Applied'] = self.calculate_days_since_applied(app['Application Date'])
                app['Success Score'] = self.calculate_success_score(app['Status'], int(app['Days Since Applied']))
                app['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated_app = app
                break

        # Write back to CSV
        if updated_app:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(applications)

        return updated_app

    def get_analytics(self) -> Dict[str, Any]:
        """Generate analytics and insights"""
        applications = self.load_applications()

        if not applications:
            return {
                'total_applications': 0,
                'message': 'No applications tracked yet'
            }

        total = len(applications)

        # Status breakdown
        status_counts = {}
        for app in applications:
            status = app['Status']
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate metrics
        interviewed = sum(1 for app in applications if app['Status'] in [
            'Interviewed', 'Second Interview', 'Interview Scheduled'
        ])
        offers = sum(1 for app in applications if app['Status'] == 'Offer Received')
        accepted = sum(1 for app in applications if app['Status'] == 'Accepted')
        rejected = sum(1 for app in applications if app['Status'] == 'Rejected')

        # Success rates
        interview_rate = (interviewed / total * 100) if total > 0 else 0
        offer_rate = (offers / total * 100) if total > 0 else 0
        acceptance_rate = (accepted / total * 100) if total > 0 else 0
        rejection_rate = (rejected / total * 100) if total > 0 else 0

        # Average days since applied
        total_days = sum(int(app['Days Since Applied']) for app in applications)
        avg_days = total_days / total if total > 0 else 0

        # Active applications (not rejected or accepted)
        active = sum(1 for app in applications if app['Status'] not in ['Rejected', 'Accepted', 'Withdrawn'])

        # Applications needing follow-up
        needs_followup = []
        today = datetime.now()
        for app in applications:
            if app['Follow-up Date']:
                try:
                    followup_date = datetime.strptime(app['Follow-up Date'], '%Y-%m-%d')
                    if followup_date <= today and app['Status'] not in ['Rejected', 'Accepted']:
                        needs_followup.append({
                            'company': app['Company Name'],
                            'job_title': app['Job Title'],
                            'followup_date': app['Follow-up Date'],
                            'days_overdue': (today - followup_date).days
                        })
                except:
                    pass

        # Top companies by success score
        companies_scores = {}
        for app in applications:
            company = app['Company Name']
            score = int(app['Success Score'])
            if company not in companies_scores:
                companies_scores[company] = []
            companies_scores[company].append(score)

        top_companies = sorted(
            [(company, sum(scores) / len(scores)) for company, scores in companies_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total_applications': total,
            'active_applications': active,
            'status_breakdown': status_counts,
            'metrics': {
                'interview_rate': round(interview_rate, 1),
                'offer_rate': round(offer_rate, 1),
                'acceptance_rate': round(acceptance_rate, 1),
                'rejection_rate': round(rejection_rate, 1)
            },
            'average_days_since_applied': round(avg_days, 1),
            'needs_followup': needs_followup,
            'top_companies': [{'company': c, 'avg_score': round(s, 1)} for c, s in top_companies]
        }

    def get_applications_needing_action(self) -> Dict[str, List]:
        """Get applications that need action"""
        applications = self.load_applications()
        today = datetime.now()

        needs_followup = []
        upcoming_interviews = []
        stale_applications = []

        for app in applications:
            # Skip closed applications
            if app['Status'] in ['Rejected', 'Accepted', 'Withdrawn']:
                continue

            # Check follow-up date
            if app['Follow-up Date']:
                try:
                    followup_date = datetime.strptime(app['Follow-up Date'], '%Y-%m-%d')
                    if followup_date <= today:
                        needs_followup.append(app)
                except:
                    pass

            # Check upcoming interviews
            if app['Interview Date']:
                try:
                    interview_dt = datetime.strptime(app['Interview Date'], '%Y-%m-%d %H:%M:%S')
                    if today <= interview_dt <= today + timedelta(days=7):
                        upcoming_interviews.append(app)
                except:
                    pass

            # Check stale applications (applied > 14 days, no response)
            days = int(app['Days Since Applied'])
            if app['Status'] == 'Applied' and days > 14:
                stale_applications.append(app)

        return {
            'needs_followup': needs_followup,
            'upcoming_interviews': upcoming_interviews,
            'stale_applications': stale_applications
        }

    def export_to_csv(self, filename: str = None) -> str:
        """Export current data to CSV"""
        if filename is None:
            filename = f'job_applications_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        applications = self.load_applications()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(applications)

        return filename


def generate_status_color_code(status: str) -> str:
    """Return hex color code for status"""
    colors = {
        'Applied': '#FFB84D',           # Orange
        'Phone Screen': '#4DA6FF',      # Light Blue
        'Interview Scheduled': '#6B8EFF', # Blue
        'Interviewed': '#9D7EFF',       # Purple
        'Second Interview': '#B066FF',  # Deep Purple
        'Offer Received': '#66FF99',    # Light Green
        'Accepted': '#00CC66',          # Green
        'Rejected': '#FF6B6B',          # Red
        'Withdrawn': '#999999',         # Gray
        'Follow-up Needed': '#FFD93D'   # Yellow
    }
    return colors.get(status, '#CCCCCC')


if __name__ == '__main__':
    # Example usage
    tracker = JobTrackerManager()
    print("Job Application Tracker initialized successfully!")
