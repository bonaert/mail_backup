import os
import imaplib
import email
import quopri
import getpass
from bs4 import BeautifulSoup
from pprint import pprint


def get_server():
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    my_email = raw_input('Insert your email: ')
    my_pass = getpass.getpass('Insert your password: ')

    print("Logging in")
    server.login(my_email, my_pass)
    print("Getting emails")
    server.select()
    return server


def get_messages(server):
    messages = []

    resp, msg_data = server.uid('FETCH', '1:*', '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            messages.append(email.message_from_string(response_part[1]))

    return messages


def get_bodies(messages):
    return [message.as_string() for message in messages]


def get_payloads(messages):
    payloads = []

    for message in messages:
        payloads.append(get_message_payloads(message))

    return payloads


def get_message_payloads(message):
    message_payloads = []
    if message.is_multipart():
        for part in message.get_payload():
            message_payloads.extend(get_message_payloads(part))
    else:
        message_payloads.append(message.get_payload())

    return message_payloads


def save_messages(messages):
    create_emails_directory()
    payloads = get_payloads(messages)

    for (i, message_payloads) in enumerate(payloads):

        # Usually the second payload has what we want
        if (len(message_payloads) == 1):
            payload = message_payloads[0]
        else:
            payload = message_payloads[1]

        text = quopri.decodestring(payload)
        if text:
            f = open('./emails/Email ' + str(i) + '.html', 'w')
            f.write(str(text))
            f.close()

def create_emails_directory():
	if not os.path.exists('./emails'):
		os.makedirs('./emails')

def get_messages_and_save_them():
    server = get_server()
    messages = get_messages(server)
    pprint(messages)
    save_messages(messages)

get_messages_and_save_them()
