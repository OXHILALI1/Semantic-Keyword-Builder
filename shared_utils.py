from typing import Optional, Set, Dict

SERVICE_MAPPING: Dict[str, str] = {
    'webhook': 'Webhook',
    'httprequest': 'HTTP',
    'cron': 'Cron',
    'gmail': 'Gmail',
    'slack': 'Slack',
    'googlesheets': 'GoogleSheets',
    'airtable': 'Airtable',
    'notion': 'Notion',
    'telegram': 'Telegram',
    'discord': 'Discord',
    'twitter': 'Twitter',
    'github': 'GitHub',
    'hubspot': 'HubSpot',
    'salesforce': 'Salesforce',
    'stripe': 'Stripe',
    'shopify': 'Shopify',
    'trello': 'Trello',
    'asana': 'Asana',
    'clickup': 'ClickUp',
    'calendly': 'Calendly',
    'zoom': 'Zoom',
    'mattermost': 'Mattermost',
    'microsoftteams': 'Teams',
    'googlecalendar': 'GoogleCalendar',
    'googledrive': 'GoogleDrive',
    'dropbox': 'Dropbox',
    'onedrive': 'OneDrive',
    'aws': 'AWS',
    'azure': 'Azure',
    'googlecloud': 'GCP',
    'postgresql': 'PostgreSQL',
    'mysql': 'MySQL',
    'mongodb': 'MongoDB',
    'redis': 'Redis',
    'elasticsearch': 'Elasticsearch',
    'typeform': 'Typeform',
    'mailchimp': 'Mailchimp',
    'sendgrid': 'SendGrid',
    'twilio': 'Twilio',
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'replicate': 'Replicate'
}

UTILITY_NODES: Set[str] = {
    'Set', 'Function', 'If', 'Switch', 'Merge', 'StickyNote',
    'NoOp', 'Code', 'Execute', 'Split', 'Wait', 'Stop',
}

def get_clean_service_name(raw_service_name: str) -> Optional[str]:
    """Cleans a raw service name using the mapping and filters out utility nodes."""
    # Normalize the input for mapping lookup
    normalized_raw_service = raw_service_name.lower()

    # Get from mapping or title case the original if not found
    if normalized_raw_service in SERVICE_MAPPING:
        clean_service = SERVICE_MAPPING[normalized_raw_service]
    else:
        # If not in mapping, title case the original raw service name
        clean_service = raw_service_name.title()

    # Filter out utility nodes
    # Check against common variations that might occur if not in mapping
    if clean_service in UTILITY_NODES or raw_service_name in UTILITY_NODES or raw_service_name.title() in UTILITY_NODES:
        return None

    return clean_service
