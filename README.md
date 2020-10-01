# Backup and Restore scripts for Gophish

This repo contains scripts to create and restore best-effort backups from a Gophish instance.

The script uses the official Python library where possible to interact with Gophish.

The backup contains sending profiles, landing pages and mail templates. This comes in handy to migrate or deploy
your hand-crafted templates. Users, campaigns, etc., are not saved.
Therefore, if you just need something for archiving your instance, backing up the database is certainly the way to go.

## Requirements

Python 3 (written and tested with 3.7.3) and the gophish bindings. You can install them using pip: `pip install -r requirements.txt`

## Usage

### Backup

~~~bash
python3 ./gophish-backup.py --instance https://my.phishingserver.tld/ --api-key 1234567890
~~~

A `--filename` argument is optional.

### Restore

~~~bash
python3 ./gophish-restore.py --instance https://my.phishingserver.tld/ --api-key 1234567890
~~~
