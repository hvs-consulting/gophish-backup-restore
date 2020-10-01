#!/usr/bin/env python3

import argparse
import sys
import json
import zipfile
import backup_utils
import gophish


'''
A sending profile has the following attributes:
- from_address: string
- host: string
- id: uint
- ignore_cert_errors: bool
- interface_type: string (usually 'SMTP')
- modified_date: datetime.datetime 
- name: string
For modified_date, it is probably best to convert it to ISO8601 
'''
def backup_sending_profiles(api, zf):
    for smtp in api.smtp.get():
        sending_profile_dict = smtp.as_dict()
        identifier = sending_profile_dict['id']
        zf.writestr('sending_profiles/{0}/sending_profile_{0}.json'.format(identifier), json.dumps(sending_profile_dict, sort_keys=True, default=str))

'''
A mail template has the following attributes:
- id: uint
- modified date: datetime.datetime
- name: string
- subject: string
- html: string
- text: string
- attachements: dict
For HTML, it makes sense to write this in a separate file and reference it here
'''
def backup_templates(api, zf):
    for template in api.templates.get():
        template_dict = template.as_dict()
        attachments = []
        identifier = template_dict['id']
        html = template_dict.get('html')
        text = template_dict.get('text')
        if template_dict.get('attachments') is not None:
            # For some reason, attachments are not contained in the object if not fetched explicitly via id
            attachments = api.templates.get(identifier).attachments
        if html is not None:
            template_dict.pop('html')
            zf.writestr('templates/{0}/template_{0}.html'.format(identifier), html)
        if text is not None:
            template_dict.pop('text')
            zf.writestr('templates/{0}/template_{0}.txt'.format(identifier), text)
        for count, attachment in enumerate(attachments):
            zf.writestr('templates/{0}/attachments/{1}.json'.format(identifier, count), json.dumps({'name': attachment.name, 'type': attachment.type, 'content': attachment.content}))
        zf.writestr('templates/{0}/template_{0}.json'.format(identifier), json.dumps(template_dict, sort_keys=True, default=str))


'''
A landing page has the following attributes:
id: uint
name: string
html: string
modified_date: datetime.datetime
capture_credentials: bool
capture_passwords: bool
redirect_url: string
For HTML, it makes sense to write this in a separate file and reference it here
'''
def backup_landing_pages(api, zf):
    for page in api.pages.get():
        page_dict = page.as_dict()
        identifier = page_dict['id']
        html = page_dict.get('html')
        if html is not None:
            page_dict.pop('html')
            zf.writestr('pages/{0}/page_{0}.html'.format(identifier), html)
        zf.writestr('pages/{0}/page_{0}.json'.format(identifier), json.dumps(page_dict, sort_keys=True, default=str))


def perform_backup(api, filename):
    with zipfile.ZipFile(filename, 'w') as zf:
        backup_sending_profiles(api, zf)
        backup_templates(api, zf)
        backup_landing_pages(api, zf)


def main():
    parser = argparse.ArgumentParser(description='Create a backup of a Gophish instance')
    parser.add_argument('--instance', required=True, type=str, help='URI of your instance, e.g. https://my.phishingserver.tld/')
    parser.add_argument('--api-key', required=True, help='Your API key')
    parser.add_argument('--filename', required=False, help='Filename of the backup')
    args = parser.parse_args()
    backup_utils.check_host(args.instance)
    api = gophish.Gophish(args.api_key, host=args.instance)
    filename = 'gophish_backup.zip'
    if args.filename is not None:
        if args.filename.endswith('.zip'):
            filename = args.filename
        else:
            filename = args.filename + '.zip'        
    perform_backup(api, filename)

if __name__ == '__main__':
    main()