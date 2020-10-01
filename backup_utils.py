import sys

def check_host(raw_target):
    if not (raw_target.startswith("http://") or raw_target.startswith("https://")):
        print("Instance must start with http:// or https:// - e.g. https://my.phishingserver.tld/")
        sys.exit(1)
    if not (raw_target.endswith("/")):
        print("Path is invalid. Please provide the full URI with leading slashes, e.g. https://my.phishingserver.tld/")
        sys.exit(1)