"""
AI Assistant for Job Application Tracker
Generates follow-up emails, summarizes interviews, and provides suggestions
"""

from datetime import datetime
from typing import Dict, List, Any


class JobApplicationAI:
    """AI-powered assistant for job applications"""

    @staticmethod
    def generate_followup_email(application: Dict[str, Any]) -> Dict[str, str]:
        """Generate a professional follow-up email"""
        company = application.get('Company Name', '')
        job_title = application.get('Job Title', '')
        contact_person = application.get('Contact Person', 'Hiring Manager')
        app_date = application.get('Application Date', '')
        status = application.get('Status', '')
        days_since = application.get('Days Since Applied', 0)

        # Calculate how long ago they applied
        try:
            app_datetime = datetime.strptime(app_date, '%Y-%m-%d')
            time_phrase = f"{days_since} days ago"
            if days_since == 1:
                time_phrase = "yesterday"
            elif days_since < 7:
                time_phrase = f"{days_since} days ago"
            elif days_since < 14:
                time_phrase = "last week"
            elif days_since < 30:
                time_phrase = f"{days_since // 7} weeks ago"
            else:
                time_phrase = f"{days_since // 30} months ago"
        except:
            time_phrase = "recently"

        # Different templates based on status
        templates = {
            'Applied': {
                'subject': f'Following Up on {job_title} Application - [Your Name]',
                'body': f"""Dear {contact_person},

I hope this email finds you well. I wanted to follow up on my application for the {job_title} position at {company}, which I submitted {time_phrase}.

I remain very interested in this opportunity and believe my skills and experience would make me a strong fit for your team. I'm particularly excited about [mention something specific about the role or company that interests you].

I would welcome the opportunity to discuss how I can contribute to {company}'s success. Please let me know if you need any additional information from me.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
[Your Name]
[Your Phone]
[Your Email]"""
            },

            'Phone Screen': {
                'subject': f'Thank You - {job_title} Phone Interview',
                'body': f"""Dear {contact_person},

Thank you for taking the time to speak with me {time_phrase} about the {job_title} position at {company}. I enjoyed learning more about the role and your team.

Our conversation reinforced my enthusiasm for this opportunity. I'm particularly excited about [mention something specific from the conversation].

I'm very interested in moving forward in the process and would be happy to provide any additional information you may need. Please feel free to reach out if you have any questions.

Thank you again for your consideration. I look forward to the next steps.

Best regards,
[Your Name]"""
            },

            'Interviewed': {
                'subject': f'Thank You - {job_title} Interview Follow-Up',
                'body': f"""Dear {contact_person},

I wanted to reach out and thank you again for the interview for the {job_title} position at {company}. It was a pleasure meeting with you and learning more about the role and the team.

I remain very excited about the opportunity and am confident that my experience in [relevant skill/area] would enable me to make meaningful contributions to your team.

I wanted to check in on the status of my application and the next steps in your hiring process. Please let me know if you need any additional information from me.

Thank you for your time and consideration.

Best regards,
[Your Name]"""
            },

            'Follow-up Needed': {
                'subject': f'Checking In - {job_title} Application Status',
                'body': f"""Dear {contact_person},

I hope you're doing well. I wanted to reach out regarding my application for the {job_title} position at {company}.

I remain highly interested in this opportunity and would appreciate any update you might have on the hiring process and timeline.

If there's any additional information I can provide to support my application, please don't hesitate to let me know.

Thank you for your time, and I look forward to hearing from you.

Best regards,
[Your Name]"""
            }
        }

        template = templates.get(status, templates['Applied'])

        return {
            'subject': template['subject'],
            'body': template['body'],
            'recipient': application.get('Contact Email', ''),
            'tips': [
                '📝 Personalize: Add specific details from your research or previous conversations',
                '✏️ Customize: Replace [Your Name], [Your Phone], [Your Email] with your actual information',
                '🎯 Be specific: Reference particular projects or aspects of the role that excite you',
                '⏰ Timing: Best to send follow-ups on Tuesday-Thursday mornings',
                '📧 Keep it brief: Hiring managers are busy - respect their time'
            ]
        }

    @staticmethod
    def summarize_interview_notes(notes: str, job_title: str, company: str) -> Dict[str, Any]:
        """Summarize interview notes with key insights"""
        if not notes or len(notes.strip()) < 10:
            return {
                'summary': 'No interview notes available to summarize.',
                'key_points': [],
                'action_items': [],
                'red_flags': [],
                'positive_signals': []
            }

        # This is a template - in a full implementation, you'd use actual AI/NLP
        # For now, provide a structured format users can fill in
        return {
            'summary': f'Interview Summary for {job_title} at {company}',
            'structure': {
                'Overview': 'Brief overview of the interview (who you met, format, duration)',
                'Key Discussion Points': [
                    'Main topics covered during the interview',
                    'Questions they asked you',
                    'Questions you asked them'
                ],
                'Technical Assessment': 'If applicable, what technical questions or challenges were discussed',
                'Cultural Fit': 'Your impressions of company culture and team dynamics',
                'Compensation & Benefits': 'Any discussion about salary, benefits, or perks',
                'Next Steps': 'What they said about timeline and next steps'
            },
            'action_items': [
                'Send thank-you email within 24 hours',
                'Research any topics mentioned that you need to learn more about',
                'Prepare materials they requested (portfolio, references, etc.)',
                'Set follow-up reminder if you don\'t hear back in their stated timeline'
            ],
            'evaluation_framework': {
                'Positive Signals': [
                    '✅ Discussed specific projects you\'d work on',
                    '✅ Introduced you to other team members',
                    '✅ Asked about your availability or start date',
                    '✅ Discussed compensation or benefits',
                    '✅ Spent more time than scheduled',
                    '✅ Asked detailed questions about your experience'
                ],
                'Red Flags': [
                    '🚩 Couldn\'t clearly explain the role',
                    '🚩 Mentioned high turnover',
                    '🚩 Unrealistic expectations or workload',
                    '🚩 Poor communication or disorganization',
                    '🚩 Vague about compensation',
                    '🚩 Negative comments about current/former employees'
                ]
            },
            'raw_notes': notes
        }

    @staticmethod
    def get_application_suggestions(application: Dict[str, Any], all_applications: List[Dict]) -> Dict[str, List[str]]:
        """Provide AI-powered suggestions to improve job search"""
        suggestions = {
            'immediate_actions': [],
            'strategy_tips': [],
            'warnings': [],
            'optimizations': []
        }

        status = application.get('Status', '')
        days_since = int(application.get('Days Since Applied', 0))
        company = application.get('Company Name', '')
        job_title = application.get('Job Title', '')

        # Immediate action suggestions
        if status == 'Applied' and days_since >= 7:
            suggestions['immediate_actions'].append(
                f'🔔 It\'s been {days_since} days since you applied. Consider sending a follow-up email.'
            )

        if status == 'Applied' and days_since >= 14:
            suggestions['immediate_actions'].append(
                '🔍 Try finding employees at the company on LinkedIn and asking about the role.'
            )

        if not application.get('Follow-up Date'):
            suggestions['immediate_actions'].append(
                '📅 Set a follow-up date (typically 7-10 days after applying) to stay organized.'
            )

        if not application.get('Contact Person'):
            suggestions['immediate_actions'].append(
                '👤 Try to find the hiring manager\'s name on LinkedIn or the company website.'
            )

        if status in ['Interview Scheduled', 'Interviewed']:
            suggestions['immediate_actions'].append(
                '📚 Research the company thoroughly - recent news, products, culture, and competitors.'
            )
            suggestions['immediate_actions'].append(
                '💡 Prepare STAR method examples for common behavioral questions.'
            )

        # Strategy tips based on overall pattern
        total_apps = len(all_applications)
        if total_apps >= 5:
            # Analyze patterns
            status_counts = {}
            for app in all_applications:
                st = app.get('Status', 'Applied')
                status_counts[st] = status_counts.get(st, 0) + 1

            interviews = status_counts.get('Interviewed', 0) + status_counts.get('Interview Scheduled', 0)
            interview_rate = (interviews / total_apps * 100) if total_apps > 0 else 0

            if interview_rate < 10:
                suggestions['strategy_tips'].append(
                    '📊 Low interview rate (<10%). Consider: tailoring your resume more, improving your cover letter, or targeting roles that better match your experience.'
                )

            if status_counts.get('Applied', 0) > total_apps * 0.7:
                suggestions['strategy_tips'].append(
                    '🎯 Most applications are still in "Applied" status. Try: following up more actively, networking to get referrals, or applying to roles where you have connections.'
                )

        # Warnings
        if days_since > 30 and status == 'Applied':
            suggestions['warnings'].append(
                f'⚠️ It\'s been over a month with no response from {company}. Consider moving this to "Rejected" and focusing energy elsewhere.'
            )

        if status == 'Interview Scheduled' and not application.get('Interview Date'):
            suggestions['warnings'].append(
                '⚠️ You marked this as "Interview Scheduled" but no interview date is set. Update the interview date field.'
            )

        # Optimization tips
        suggestions['optimizations'].append(
            '🔗 Connect with employees at target companies on LinkedIn before applying.'
        )
        suggestions['optimizations'].append(
            '✍️ Customize your resume and cover letter for each application - highlight relevant keywords from the job description.'
        )
        suggestions['optimizations'].append(
            '📧 If you have an email from the company (even automated), reply to it rather than sending a cold email.'
        )
        suggestions['optimizations'].append(
            f'🎓 Research common interview questions for {job_title} roles and prepare answers.'
        )

        return suggestions

    @staticmethod
    def generate_interview_prep_checklist(application: Dict[str, Any]) -> List[str]:
        """Generate interview preparation checklist"""
        company = application.get('Company Name', 'the company')
        job_title = application.get('Job Title', 'this role')

        return [
            f'✅ Research {company}: mission, values, recent news, products/services, competitors',
            f'✅ Review the job description for {job_title} and identify key requirements',
            '✅ Prepare 5-7 STAR method examples showcasing your relevant experience',
            '✅ Prepare questions to ask the interviewer (about role, team, culture, growth)',
            '✅ Review your resume and be ready to discuss every point in detail',
            '✅ Practice common interview questions out loud',
            f'✅ Research your interviewer on LinkedIn (if you know who it is)',
            '✅ Prepare your workspace (if virtual) or plan your route (if in-person)',
            '✅ Test your tech setup (camera, mic, internet) if virtual interview',
            '✅ Plan your outfit (professional and comfortable)',
            '✅ Print extra copies of your resume and have a notepad ready',
            '✅ Prepare a brief 30-60 second "tell me about yourself" pitch',
            '✅ Have examples ready of: leadership, teamwork, conflict resolution, and problem-solving',
            '✅ Research typical salary range for this role in your location',
            '✅ Prepare thoughtful questions about the role, team dynamics, and success metrics'
        ]


def generate_weekly_summary(applications: List[Dict[str, Any]]) -> str:
    """Generate a weekly summary of job search activity"""
    from datetime import datetime, timedelta

    today = datetime.now()
    week_ago = today - timedelta(days=7)

    # Filter this week's activity
    recent_apps = []
    for app in applications:
        try:
            last_updated = datetime.strptime(app.get('Last Updated', ''), '%Y-%m-%d %H:%M:%S')
            if last_updated >= week_ago:
                recent_apps.append(app)
        except:
            pass

    summary = f"""
📊 **Weekly Job Search Summary** ({week_ago.strftime('%b %d')} - {today.strftime('%b %d, %Y')})

📝 **Activity This Week:**
- {len(recent_apps)} applications updated or added
- Total active applications: {len([a for a in applications if a['Status'] not in ['Rejected', 'Accepted', 'Withdrawn']])}

📈 **Progress:**
"""

    # Status breakdown for this week
    status_counts = {}
    for app in recent_apps:
        status = app.get('Status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        summary += f"- {status}: {count}\n"

    summary += "\n💪 **Keep going! Consistency is key in job searching.**"

    return summary
