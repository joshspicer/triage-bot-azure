import logging
from github import Github 
from datetime import date
import os
import requests

import azure.functions as func

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
    if "SLACK_HOOK" not in env or "GITHUB_TOKEN" not in env:
        logging.error("[-] Must export SLACK_HOOK and GITHUB_TOKEN variables")
        exit(1)

    ghtoken = os.environ.get("GITHUB_TOKEN")
    g = Github(ghtoken)

    DAYS_OLD_LIMIT = 50

    REPOS = ["xamarin/designer", "xamarin/babyshark"]

    team = {
            'Bret' :     ('<@U1A0AGACW>', "BretJohnson"),
            'Stephen':   ('<@U03CEGTKL>', "decriptor"),
            'Josh':      ('<@UV2KCSKD1>', "joshspicer"),
            'Jérémie':   ('<@U03CFD02U>', "garuma"),
            'Dominique': ('<@U03CDPF7K>', "CartBlanche"),
            'Michael' :  ('<@UKWB26ECB>', "mcumming")
            }
            
    msg = "⚠️ *PRs Pending Review*\n\n"
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
            person = [value[0] for (key, value) in team.items() if value[1] in reviewers]

            if (not pr_is_draft and len(person) > 0):
                slack_ids = ", ".join(person)
                days_old = (date.today() - pr_date.date()).days

                if days_old < DAYS_OLD_LIMIT:
                    msg += f"{slack_ids}!  Your review is requested on <{pr_url}|{pr_name} *(#{pr_num})*>\n"

    slack_hook = os.environ.get('SLACK_HOOK')
    requests.post(slack_hook, json={"text": msg})