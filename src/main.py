from imap_tools import MailBox, AND
from configparser import ConfigParser
import requests
import time
import re


config = ConfigParser()
config.read('mail.ini')


headers = {
    "Content-Type": "application/json"
}


def trim(regex, text):
    m = re.search(regex, text)
    if m is not None:
        return m.start()
    return None


def login():
    server = config['CREDENTIALS']['SERVER']
    username = config['CREDENTIALS']['USERNAME']
    password = config['CREDENTIALS']['PASSWORD']
    return MailBox(server).login(username, password)


def contain(arr):
    return any(config['DISCORD']['ADDRESS'] == element for element in arr)


def read(box):
    messages = box.fetch(AND(seen=False))
    for msg in messages:
        if contain(msg.to):
            yield msg


def send(msg):
    text = msg.text
    index = trim(re.compile(r"[a-z]{2} [0-9]+\. [0-9]+\. 20[0-9]{2} (v )*[0-9]{2}:[0-9]{2}"), text)
    if index is not None:
        text = text[:index]
    author = {
        "name": msg.from_
    }
    embed = {
        "description": text,
        "title": msg.subject,
        "color": 0xee00ee,
        "author": author
    }

    data = {
        "username": config['DISCORD']["NAME"],
        "embeds": [embed]
    }

    return requests.post(config['DISCORD']['WEBHOOK'], json=data, headers=headers)


def error(status):
    raise UnableToSendMessageError("Unable to send message, status: " + str(status))

class UnableToSendMessageError(Exception):
    pass

def worker():
    box = login()
    for msg in read(box):
        status = send(msg).status_code
        if status != 204:
            error(status)

if __name__ == '__main__':
    worker()
