import requests
import os
import logging
from datetime import date

import azure.functions as func


def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    feedback_triage()


def feedback_triage():

    env = os.environ.copy()
    if "TEAMS_HOOK" not in env or "FEEDBACK_URL" not in env:
        logging.error(
            "[-] Must export TEAMS_HOOK and FEEDBACK_URL env variable Exiting...")
        exit(1)

    feedback_url = os.environ.get("FEEDBACK_URL")

    names = ['Bret',
             'Stephen',
             'Josh',
             'Jérémie',
             'Dominique',
             'Michael']

    length = len(names)
    d = date.today()
    week_num = d.isocalendar()[1]

    assigned = names[week_num % length]
    onDeck = names[(week_num + 1) % length]
    following = names[(week_num + 2) % length]

    debug_str = f"[+] week={week_num}  assignments={assigned}, {onDeck}, {following}"
    logging.info(debug_str)

    content = '''
{{
"@type": "MessageCard",
"@context": "http://schema.org/extensions",
"themeColor": "ff0000",
"summary": "Feedback Triage Duty!",
"sections": [{{
    "activityTitle": "#**Feedback Triage Duty**",
    "facts": [{{
        "name": "On Duty",
        "value": "{0}"
    }},
    {{
        "name": "Next",
        "value": "{1}"
    }},
    {{
        "name": "Following",
        "value": "{2}"
    }}],
    "markdown": true
}}],
"potentialAction": [{{
    "@type": "OpenUri",
    "name": "Go to Dashboard",
    "targets": [
    {{"os": "default", "uri": "{3}"}}
    ]}}]
}}
'''.format(assigned, onDeck, following, feedback_url)

    teams_hook = os.environ.get('TEAMS_HOOK')
    r = requests.post(teams_hook, data=content)
