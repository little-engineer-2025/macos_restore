#!/usr/bin/env python3
import requests

LINK = 'https://mesu.apple.com/assets/macos/com_apple_macOSIPSW/com_apple_macOSIPSW.xml'

def figure_out_url(data, model:str) -> str:
    assert data is not None, 'data is None'
    assert model is not None and model != '', 'model is not provided'
    return data

def download_com_apple_macosipsw_xml() -> str:
    r = requests.get(LINK)
    assert r.status_code == 200, 'Expected a 200 return code: please check your network'
    return r.text
