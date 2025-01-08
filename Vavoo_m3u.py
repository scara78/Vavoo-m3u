#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             28/12/2024               *
****************************************
# --------------------#
# Info Linuxsat-support.com & corvoboys.org

USAGE:
put this file in to /tmp  
telnet command
---> cd /tmp
---> python Vavoo_m3u.py

explore folder VavooGen


'''
import os
import requests
import json

# Funzione per generare contenuto M3U per un singolo elemento
def generate_m3u(group, name, logo, tvg_id, url):
    # Modifiche agli URL
    url = url.replace(".ts", "/index.m3u8").replace("/live2/play", "/play")
    if ".ts" in url:
        url = url.replace(".ts", "/index.m3u8")
    if not url.endswith("/index.m3u8"):
        url += "/index.m3u8"
    url = url.replace(".m3u8.m3u8", ".m3u8")
    # url = url.replace("https://vavoo.to/play/", "https://joaquinito02.es/vavoo/", 1)
    url = url.replace("/index.m3u8", ".m3u8", 1)

    m3u_entry = (
        "#EXTINF:-1 tvg-id=\"{}\" tvg-name=\"{}\" tvg-logo=\"{}\" group-title=\"{}\" "
        "http-user-agent=\"VAVOO/1.0\" http-referrer=\"https://vavoo.to/\",{}\n"
        "#EXTVLCOPT:http-user-agent=VAVOO/1.0\n"
        "#EXTVLCOPT:http-referrer=https://vavoo.to/\n"
        "#KODIPROP:http-user-agent=VAVOO/1.0\n"
        "#KODIPROP:http-referrer=https://vavoo.to/\n"
        "#EXTHTTP:{{\"User-Agent\":\"VAVOO/1.0\",\"Referer\":\"https://vavoo.to/\"}}\n"
        "{}"
    ).format(tvg_id, name, logo, group, name, url)
    return m3u_entry, url

# Funzione per scaricare i dati JSON
def fetch_json_data():
    response = requests.get("https://www2.vavoo.to/live2/index?countries=all&output=json")
    response.raise_for_status()
    return response.json()

# Funzione per elaborare un singolo elemento
def process_item(item):
    return generate_m3u(item.get("group", ""), item.get("name", ""), item.get("logo", ""), item.get("tvg_id", ""), item.get("url", ""))

# Main
def main():
    output_dir = "/"
    # output_dir = "/tmp/VavooGen"
    # os.makedirs(output_dir, exist_ok=True)

    try:
        items = fetch_json_data()
    except Exception as e:
        print("Errore durante il download dei dati JSON: {}".format(e))
        return

    # File principali
    index_m3u_path = os.path.join(output_dir, "index.m3u")
    ids_txt_path = os.path.join(output_dir, "ids.txt")

    # Rimuovi file esistenti
    if os.path.exists(index_m3u_path):
        os.remove(index_m3u_path)

    # Inizializza contenuto
    ids_content = ""
    processed_count = 0
    groups = {}

    # Scrivi contenuto iniziale nel file index.m3u
    with open(index_m3u_path, "w") as index_m3u:
        index_m3u.write("#EXTM3U\n")

    # Elabora ogni elemento
    for item in items:
        try:
            m3u_content, group, htaccess_url = process_item(item)
        except Exception as e:
            print("Errore durante l'elaborazione di un elemento: {}".format(e))
            continue

        # Scrivi nei file appropriati
        with open(index_m3u_path, "a") as index_m3u:
            index_m3u.write(m3u_content + "\n")

        if group not in groups:
            group_file_path = os.path.join(output_dir, "index_{}.m3u".format(group))
            groups[group] = group_file_path
            with open(group_file_path, "w") as group_file:
                group_file.write("#EXTM3U\n")

        with open(groups[group], "a") as group_file:
            group_file.write(m3u_content + "\n")

        # Aggiungi ID a ids.txt
        item_id = item.get("url", "").replace("https://vavoo.to/live2/play/", "").replace(".ts", "")
        ids_content += item_id + "\n"

        processed_count += 1
        print("Elaborati {}/{} canali".format(processed_count, len(items)))

    # Scrivi il file ids.txt
    with open(ids_txt_path, "w") as ids_file:
        ids_file.write(ids_content)

    print("Generazione completata. File salvati in: {}".format(output_dir))


if __name__ == "__main__":
    main()
