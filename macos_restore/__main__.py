#!/usr/bin/env python3
import io
import os
import sys
import logging
import subprocess

import requests
import plistlib
import hashlib
import urllib

logger = None

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
    assert data is not None and data != {}, "data must be an initilized dictionary"
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
    with open(filename, mode='rb') as f:
        resultado = hashlib.file_digest(f, 'sha1')
    assert resultado.hexdigest() == sha1, 'SHA1 mistmatch at "{}": expected "{}"'.format(filename, sha1)
    return True

def descargar_con_progreso(url, nombre_archivo):
    # 1. Verificar si el archivo ya existe para reanudar
    modo_archivo = "ab"  # 'a'ppend 'b'inary (añadir al final)
    bytes_locales = 0
    headers = {}

    if os.path.exists(nombre_archivo):
        bytes_locales = os.path.getsize(nombre_archivo)
        # Solicitar solo los bytes restantes
        headers['Range'] = f'bytes={bytes_locales}-'
        print(f"Resumiendo descarga desde {bytes_locales} bytes...")
    else:
        modo_archivo = "wb" # 'w'rite 'b'inary (crear nuevo)

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as respuesta:
            # Obtener el tamaño total (Content-Length del servidor + lo que ya tenemos)
            cl = respuesta.getheader('Content-Length')
            total_remoto = int(cl) if cl else 0
            total_final = total_remoto + bytes_locales

            # Si el servidor ignora el Range y devuelve 200 en vez de 206
            if respuesta.status == 200 and bytes_locales > 0:
                print("El servidor no soporta reanudación. Empezando de cero.")
                modo_archivo = "wb"
                bytes_locales = 0

            with open(nombre_archivo, modo_archivo) as f:
                descargado = bytes_locales
                bloque_size = 8192

                while True:
                    buffer = respuesta.read(bloque_size)
                    if not buffer:
                        break

                    f.write(buffer)
                    descargado += len(buffer)

                    # 2. Imprimir progreso en la misma línea
                    if total_final:
                        porcentaje = (descargado / total_final) * 100
                        progreso = f"\rDescargando: {porcentaje:.2f}% ({descargado}/{total_final} bytes)"
                    else:
                        progreso = f"\rDescargando: {descargado} bytes (tamaño total desconocido)"

                    sys.stdout.write(progreso)
                    sys.stdout.flush()

        print("\n¡Descarga completada!")

    except urllib.error.HTTPError as e:
        if e.code == 416: # Range Not Satisfiable (ya está completo)
            print("\nEl archivo ya parece estar completo.")
        else:
            print(f"\nError HTTP: {e.code}")

def download(url: str, sha1: str):
    assert url != '' and url != None, 'url is required'
    output_file = os.path.basename(url)
    print(">> Downloading '{}'".format(url))
    descargar_con_progreso(url, output_file)

    if sha1 is not None:
        print(">> Checking hash '{}'".format(sha1))
        check_sha1sum(output_file, sha1)
    with open(output_file, "rb") as fr:
        result = fr.read()
    return result

def setup_logging():
    global logger
    logger = logging.getLogger("macos_restore")
    logging.basicConfig(filename='macos_restore.log', encoding='utf-8', level=logging.DEBUG)

def main():
    setup_logging()
    logging.info("macos_restore started")
    assert len(sys.argv) == 2, _.ERR_PRODUCT_NAME_MISSED

    # Download and verify metadata
    logger.info("downloading metadata")
    product = sys.argv[1]
    body_text = download(_.LINK, sha1=None)

    logger.info("searching product")
    assert len(sys.argv) == 2, _.PRODUCT_NAME_MISSED

    plist = plistlib.loads(body_text, fmt=plistlib.FMT_XML)
    data = entry_from_product(plist, product)
    download(data[_.FIRMWARE_URL], data[_.FIRMWARE_SHA1])

if __name__ == '__main__':
    main()

