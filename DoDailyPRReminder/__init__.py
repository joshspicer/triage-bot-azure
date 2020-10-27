import logging
from github import Github
from datetime import date
import os
import requests

import azure.functions as func


def sanitize(input: str) -> str:
    return input.replace("\"", "\'") 

def main(mytimer: func.TimerRequest) -> None:

    # Don't run on the weekend (Sat = 5, Sun = 6)
    weekend = [5, 6]
    if date.today().weekday() in weekend:
        logging.info("It's the weekend!")
        return

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran.')

    pr_reminder()


def pr_reminder():

    env = os.environ.copy()
    if "TEAMS_HOOK" not in env or "GITHUB_TOKEN" not in env:
        logging.error("[-] Must export TEAMS_HOOK and GITHUB_TOKEN variables")
        exit(1)

    ghtoken = os.environ.get("GITHUB_TOKEN")
    g = Github(ghtoken)

    DAYS_OLD_LIMIT = 50

    REPOS = ["xamarin/uitools",
             "xamarin/ios-sim-sharp", "xamarin/Xamarin.PropertyEditing"]

    team = {
        'Michael':   ('Michael', "mcumming"),
        'Josh':      ('Josh', "joshspicer"),
        'Stephen':   ('Stephen', "decriptor"),
        'Bret':      ('Bret', "BretJohnson")
    }
    msgs = []
    for repo in REPOS:
        p = g.get_repo(repo)

        for pull in p.get_pulls():

            pr_num = pull.number
            pr_name = (pull.title)
            pr_url = pull.html_url
            pr_date = pull.created_at
            pr_is_draft = pull.draft

            reviewers = [p.login for p in pull.get_review_requests()[0]]

            # Only add if member is part of team
            person = [value[0]
                      for (key, value) in team.items() if value[1] in reviewers]

            if (not pr_is_draft and len(person) > 0):
                reviewer_names = ", ".join(person)
                days_old = (date.today() - pr_date.date()).days

                if days_old < DAYS_OLD_LIMIT:
                    num_reviewers = len(person)
                    msgs.append((reviewer_names, pr_url, pr_name, pr_num, num_reviewers))
                    # msg += f"{reviewer_names}!  Your review is requested on <{pr_url}|{pr_name} *(#{pr_num})*>\n"

    body = ""
    for idx, msg in enumerate(msgs):
        is_last_element = idx == len(msgs) - 1

        targets = msg[0] if msg[4] < 3 else f"{msg[4]}+ reviewers"
        
        body += '''
        {{
        "name": "{}",
        "value": "[{}]({})"
         }}
        '''.format(sanitize(targets), sanitize(msg[2]), sanitize(msg[1]))

        if not is_last_element:
            body += ","


# https://messagecardplayground.azurewebsites.net/
    content = '''
{{
"@type": "MessageCard",
"@context": "http://schema.org/extensions",
"themeColor": "ff0000",
"summary": "PR Bot",
"sections": [{{
    "activityTitle": "# ⚠️ **PRs Pending Review** ⚠️",
    "facts": [{}],
    "markdown": true
}}],
"potentialAction": [{{
    "@type": "OpenUri",
    "name": "Go to UITools",
    "targets": [
    {{"os": "default", "uri": "https://github.com/xamarin/uitools"}}
    ]}}]
}}
'''.format(body)

    # logging.info(content)

    teams_hook = os.environ.get('TEAMS_HOOK')
    r = requests.post(teams_hook, data=content.encode('utf-8'))

    logging.info(f"Webhook Status: {r.status_code}")
    logging.info(r.text)