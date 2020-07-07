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

    if "SLACK_HOOK" not in env:
        logging.error("[-] Must export SLACK_HOOK env variable Exiting...")
        exit(1)

    names = ['Bret',
             'Stephen',
             'Josh',
             'Jérémie',
             'Dominique',
             'Michael']

    memberIDs = ['<@U1A0AGACW>',
                 '<@U03CEGTKL>',
                 '<@UV2KCSKD1>',
                 '<@U03CFD02U>',
                 '<@U03CDPF7K>',
                 '<@UKWB26ECB>']

    if len(names) != len(memberIDs):
        logging.error("[-] Names and memberIDs do not match. Exiting...")
        exit(2)

    length = len(names)
    d = date.today()
    week_num = d.isocalendar()[1]

    assigned = names[week_num % length]
    onDeck = names[(week_num + 1) % length]
    following = names[(week_num + 2) % length]

    assigned_id = memberIDs[week_num % length]
    onDeck_id = memberIDs[(week_num + 1) % length]
    following_id = memberIDs[(week_num + 2) % length]

    debug_str = f"[+] week={week_num}  assignments={assigned}|{assigned_id}, {onDeck}|{onDeck_id}, {following}|{following_id}"
    logging.info(debug_str)

    slack_hook = os.environ.get('SLACK_HOOK')
    content = f"{assigned_id} is on feedback triage this week.  {onDeck_id} is on deck, and {following} is the following week."
    r = requests.post(slack_hook, json={"text": content})
