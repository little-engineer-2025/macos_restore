#!/usr/bin/env python3
import os
import sys

import requests
import plistlib
import subprocess

class _:
    UTF_8 = 'utf-8'
    XML_FILENAME = 'com_apple_macOSIPSW.xml'
    LINK = 'https://mesu.apple.com/assets/macos/com_apple_macOSIPSW/' + XML_FILENAME

    MOBILE_DEVICE_PRODUCT_TYPES = 'MobileDeviceProductTypes'
    MOBILE_DEVICE_SOFTWARE_VERSION_BY_VERSION = 'MobileDeviceSoftwareVersionsByVersion'
    MOBILE_DEVICE_SOFTWARE_VERSIONS = 'MobileDeviceSoftwareVersions'
    DFU = 'DFU'
    RESTORE = 'Restore'
    FIRMWARE_URL = 'FirmwareURL'
    FIRMWARE_SHA1 = 'FirmwareSHA1'

    CMD_SHA1SUM = 'sha1sum'
    CMD_CURL = 'curl'

    ERR_PRODUCT_NAME_MISSED = 'Product name missed'
    ERR_ARG_NONE = '{} is None'
    ERR_ARG_NONE_OR_EMPTY = '{} is None or empty'
    ERR_DOWNLOADING = 'Error downloading "{}": expected status_code="{}"'
    ERR_UNEXPECTED = 'unexpected error: {}'

def download_com_apple_macosipsw_xml() -> str:
    try:
        if not os.path.exists(_.XML_FILENAME):
            # Download from the network
            r = requests.get(_.LINK)
            assert r.status_code == 200, _.ERR_DOWNLOADING.format(_.LINK, r.status_code)
            with open(_.XML_FILENAME, 'w') as foutput:
                foutput.write(r.content)
        with open(_.XML_FILENAME, 'r') as finput:
            content = finput.read()
            return content
    except FileNotFoundError as e1:
        print(e1)
        return None
    except Exception as elast:
        print(_.ERR_UNEXPECTED.format(elast))
        return None

def retrieve_id_from_product(data: dict, product: str) -> str:
    for key,value in plist['MobileDeviceProductTypes'][_.DFU].items():
        if value == product:
            return key
    return None

def entry_from_product(data: dict, product: str) -> dict:
    dfus = data[_.MOBILE_DEVICE_PRODUCT_TYPES][_.DFU]
    products = data[_.MOBILE_DEVICE_SOFTWARE_VERSION_BY_VERSION]['1'][_.MOBILE_DEVICE_SOFTWARE_VERSIONS]
    download_id = list(products[product].keys())[0]
    restore = products[product][download_id][_.RESTORE]
    return restore

def check_sha1sum(filename, sha1):
    sha1_run = subprocess.run([_.CMD_SHA1SUM, filename], capture_output=True)
    sha1_calculated = sha1_run.stdout.split()[0]
    assert sha1_calculated == sha1, 'SHA1 mistmatch at "{}": expected "{}"'.format(filename, sha1)

def download(url: str, sha1: str):
    output_file = url.split("/")[-1]
    if not os.path.exists(output_file):
        result = subprocess.run([_.CMD_CURL, "-C", "-", "-O", url], stderr=sys.stderr, stdout=sys.stdout, check=True)
        if result is not None:
            assert result.returncode == 22 or result.returncode == 0, result.output
    else:
        print('info:{} already exists, if SHA1 mistmatch, delete the file and rerun'.
              format(output_file))
    if sha1 is not None:
        check_sha1sum(output_file, sha1)

def main():
    assert len(sys.argv) == 2, _.PRODUCT_NAME_MISSED
    product = sys.argv[1]
    body_text = download_com_apple_macosipsw_xml()
    plist = plistlib.loads(body_text, fmt=plistlib.FMT_XML)
    data = entry_from_product(plist, product)
    download(data[_.FIRMWARE_URL], data[_.FIRMWARE_SHA1])

if __name__ == '__main__':
    main()

