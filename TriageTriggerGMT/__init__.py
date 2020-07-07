import datetime
import logging

import azure.functions as func


def main(mytimer: func.TimerRequest, msg: func.Out[str]):

    msg.set("do the thing GMT")
