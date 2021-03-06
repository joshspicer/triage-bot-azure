# triage-bot-azure
A simple collection of azure functions to send ~slackbot~ Teams bot messages to our dev team

## Usage

This repo structure was generated by VS Code. 
The simplest way to upload these functions will be through the [Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions) extension.

These functions were developed with Python 3.7.

### Functions

#### DoDailyPRReminder
- Sends a Slack message to anybody on the team with "review requested" on our repos.
- Is triggered daily via the CRON string `0 50 13 * * *"` (Azure is in UTC).

#### DoFeedbackTriage
- Every Monday sends a message with who is on Triage duty, and the two on deck.
- Is triggered by a message on the queue (so that we can have two Cron timers).

#### TriageTriggerET & TriageTriggerGMT
- Two timer trigger functions that simply add a message to a shared queue, triggering `DoFeedbackTriage`


### Environment Variables

These variables must be set on Azure, or via a `local.settings.json` while testing locally.

*  ~`SLACK_HOOK`  : The full URI for given Slack channel to send webhook to~
*   `TEAMS_HOOK`  : The full URI for Teams webhook
*  `GITHUB_TOKEN` : A Github token with visibility into any private repos necessary
*  `FEEDBACK_URL` : The full URI for our feedback dashboard
*  `uitoolsbot_STOARGE` : Connection string for the shared Queue between functions
* `FUNCTIONS_WORKER_RUNTIME` : `python`
