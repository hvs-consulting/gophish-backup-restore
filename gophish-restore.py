#!/usr/bin/env python3

import argparse
import sys
import json
import zipfile
import backup_utils
import gophish
import requests

def restore_sending_profiles(api, zf, unsafe):
    json_files = [x for x in zf.namelist() if x.startswith('sending_profiles/') and x.endswith('.json')]
    for element in json_files:
        json_loaded = json.loads(zf.read(element))
        parsed_model = gophish.models.SMTP.parse(json_loaded) 
        try:
            api.smtp.post(parsed_model)
        except gophish.models.Error:
            if unsafe:
                api.smtp.put(parsed_model)
            else:
                print("Sending profile {0} already exists, skipping".format(json_loaded['name']))


def restore_landing_pages(api, zf, unsafe):
    filenames = zf.namelist()
    json_files = [x for x in filenames if x.startswith('pages/') and x.endswith('.json')]
    for element in json_files:
        basename = element.rstrip('.json')
        json_loaded = json.loads(zf.read(element))
        html_filename = basename + '.html'
        if html_filename in filenames:
            html = str(zf.read(html_filename))
            json_loaded['html'] = html
        parsed_model = gophish.models.Page.parse(json_loaded) 
        try:
            api.pages.post(parsed_model)
        except gophish.models.Error:
            if unsafe:
                api.pages.put(parsed_model)
            else:
                print("Page {0} already exists, skipping".format(json_loaded['name']))


def restore_templates(api, zf, unsafe):
    filenames = zf.namelist()
    json_files = [x for x in filenames if x.startswith('templates/') and x.endswith('.json') and '/attachments/' not in x]
    attachment_names = [x for x in filenames if x.startswith('templates/') and '/attachments/' in x]  
    for element in json_files: 
        basename = element.rstrip('.json')
        json_loaded = json.loads(zf.read(element))
        html_filename = basename + '.html'
        if html_filename in filenames:
            html = str(zf.read(html_filename))
            json_loaded['html'] = html
        txt_filename = basename + '.txt'
        if txt_filename in filenames:
            txt = str(zf.read(txt_filename))
            json_loaded['text'] = txt
        attachments = []
        for attachment_name in attachment_names:
            if attachment_name.startswith(basename.rsplit('/', 1)[0]+'/'):
                attachments.append((json.loads(zf.read(attachment_name))))
        if attachments:
            json_loaded['attachments'] = attachments
        
        parsed_model = gophish.models.Template.parse(json_loaded) 

        try:
            if attachments: 
                # either I'm too stupid or the client lib is broken, but restored attachments don't show up  using 
                # the client lib so we are going to set them manually via the API
                requests.post(api.client.host + "api/templates/", json=json_loaded, headers={"Authorization": api.client.api_key})
            else:
                api.templates.post(parsed_model)
        except gophish.models.Error:
            if unsafe:
                api.templates.put(parsed_model)
            else:
                print("Template {0} already exists, skipping".format(json_loaded['name']))


def perform_restore(api, filename, unsafe):
    with zipfile.ZipFile(filename, 'r') as zf:
        restore_sending_profiles(api, zf, unsafe)
        restore_templates(api, zf, unsafe)
        restore_landing_pages(api, zf, unsafe)

def perform_purge(api):
    for template in api.templates.get():
        t_id = template.as_dict()['id']
        api.templates.delete(t_id)
    for page in api.pages.get():
        p_id = page.as_dict()['id']
        api.pages.delete(p_id)
    for sending_profile in api.smtp.get():
        s_id = sending_profile.as_dict()['id']
        api.smtp.delete(s_id)
    input()


def main():
    parser = argparse.ArgumentParser(description='Restore a backup of a Gophish instance')
    parser.add_argument('--instance', required=True, type=str, help='URI of your instance, e.g. https://my.phishingserver.tld/')
    parser.add_argument('--api-key', required=True, help='Your API key')
    parser.add_argument('--filename', required=False, help='Filename of the backup')
    parser.add_argument('--unsafe', required=False, type=bool, const=True, default=False, nargs='?', help='Overwrite existing data in the instance')
    parser.add_argument('--purge', required=False, type=bool, const=True, default=False, nargs='?', help='Removes all data before doing the restore. Inteded for testing')
    args = parser.parse_args()
    backup_utils.check_host(args.instance)
    api = gophish.Gophish(args.api_key, host=args.instance)
    if args.purge:
        perform_purge(api)
    filename = 'gophish_backup.zip'
    if args.filename is not None:
        if args.filename.endswith('.zip'):
            filename = args.filename
        else:
            filename = args.filename + '.zip'        
    perform_restore(api, filename, args.unsafe)

if __name__ == '__main__':
    main()