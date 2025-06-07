#!/usr/bin/env python3
import os
import sys

from .download_xml import download_com_apple_macosipsw_xml
import plistlib
import subprocess

def retrieve_id_from_product(data: dict, product: str) -> str:
    for key,value in plist['MobileDeviceProductTypes']['DFU'].items():
        if value == product:
            return key
    return None

def entry_from_product(data: dict, product: str) -> dict:
    dfus = data['MobileDeviceProductTypes']['DFU']
    products = data['MobileDeviceSoftwareVersionsByVersion']['1']['MobileDeviceSoftwareVersions']
    restore = products[product]['24F74']['Restore']
    return restore

def download(url: str, sha1: str):
    output_file = url.split("/")[-1]
    if os.path.exists(output_file):
        sha1_run = subprocess.run(["sha1sum", output_file], capture_output=True)
        sha1_calculated = sha1_run.stdout.split()[0].decode()
        if sha1_calculated == sha1:
            return
        os.remove(output_file)
    subprocess.run(["curl", "-O", url], stderr=sys.stderr, stdout=sys.stdout)
    sha1_run = subprocess.run(["sha1sum", output_file], capture_output=True)
    assert sha1_run.stdout.split()[0] == sha1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise RuntimeException("Product name missed")
    product = sys.argv[1]
    body_text = download_com_apple_macosipsw_xml()
    plist = plistlib.loads(body_text, fmt=plistlib.FMT_XML)
    data = entry_from_product(plist, product)
    download(data['FirmwareURL'], data['FirmwareSHA1'])
