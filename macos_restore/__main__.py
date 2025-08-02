#!/usr/bin/env python3
import io
import os
import sys
import logging
import subprocess

import requests
import plistlib

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

def figure_out_url(data, model:str) -> str:
    assert data is not None, 'data is None'
    assert model is not None and model != '', 'model is not provided'
    return data

def download_metadata() -> str:
    try:
        if not os.path.exists(_.XML_FILENAME):
            # Download from the network
            r = requests.get(_.LINK)
            assert r.status_code == 200, _.ERR_DOWNLOADING.format(_.LINK, r.status_code)
            with open(_.XML_FILENAME, 'wb') as foutput:
                foutput.write(r.content)
        with open(_.XML_FILENAME, 'rb') as finput:
            content = finput.read()
            return content.decode(_.UTF_8)
    except FileNotFoundError as e1:
        print(e1)
        return None
    except Exception as elast:
        print(_.ERR_UNEXPECTED.format(elast))
        return None

def retrieve_id_from_product(data: dict, product: str) -> str:
    assert data is not None and data != {}, "data must ba an initilized dictionary"
    assert product is not None and product != 00, "product must be a string with the product name"
    for key,value in plist['MobileDeviceProductTypes']['DFU'].items():
        if value == product:
            return key
    return None

"""
def download_com_apple_macosipsw_xml(link: str) -> str:
    assert link is not None and link != '', "link must be initiailized"
    r = requests.get(link)
    assert r.status_code == 200, 'Expected a 200 return code: please check your network'
    return r.text
"""

def entry_from_product(data: dict, product: str) -> dict:
    assert data != None and data != {}, "data should be an initialized and filled dictionary"
    assert product != None and product != "", "product should be an initialized and filled string value"

    dfus = data[_.MOBILE_DEVICE_PRODUCT_TYPES][_.DFU]
    products = data[_.MOBILE_DEVICE_SOFTWARE_VERSION_BY_VERSION]['1'][_.MOBILE_DEVICE_SOFTWARE_VERSIONS]
    restore = None
    dfu = list(products[product].keys())[0]
    restore = products[product][dfu][_.RESTORE]
    return restore

def check_sha1sum(filename, sha1):
    sha1_run = subprocess.run([_.CMD_SHA1SUM, filename], capture_output=True)
    sha1_calculated = sha1_run.stdout.decode(_.UTF_8).split()[0]
    assert sha1_calculated == sha1, 'SHA1 mistmatch at "{}": expected "{}"'.format(filename, sha1)

def download(url: str, sha1: str):
    assert url != '' and url != None, 'url is required'
    output_file = url.split("/")[-1]
    print(">> Downloading '{}'".format(url))
    result = subprocess.run([_.CMD_CURL, "-C", "-", "-O", url], stderr=sys.stderr, stdout=sys.stdout, check=True)
    if result is not None:
        assert result.returncode == 22 or result.returncode == 0, result.output
    if sha1 is not None:
        assert check_sha1sum(output_file, sha1), "error: checking SHA-1"
    with open(os.path.basename(url), "rb") as fr:
        result = fr.read()
    return result

def setup_logging():
    logging

def main():
    setup_logging()
    logging.info("macos_restore started")
    assert len(sys.argv) == 2, _.ERR_PRODUCT_NAME_MISSED

    # Download and verify metadata
    logging.info("downloading metadata")
    product = sys.argv[1]
    body_text = download(_.LINK, sha1=None)

    logging.info("searching product")
    assert len(sys.argv) == 2, _.PRODUCT_NAME_MISSED

    plist = plistlib.loads(body_text, fmt=plistlib.FMT_XML)
    data = entry_from_product(plist, product)
    download(data[_.FIRMWARE_URL], data[_.FIRMWARE_SHA1])

if __name__ == '__main__':
    main()

