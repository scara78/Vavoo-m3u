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
import json
import requests

def generate_m3u(group, name, logo, tvg_id, url):
    # Modifica degli URL
    url = url.replace(".ts", "/index.m3u8").replace("/live2/play", "/play")
    if ".ts" in url:
        url = url.replace(".ts", "/index.m3u8")
    if not url.endswith("/index.m3u8"):
        url += "/index.m3u8"
    url = url.replace(".m3u8.m3u8", ".m3u8")
    url = url.replace("https://vavoo.to/play/", "https://joaquinito02.es/vavoo/")
    url = url.replace("/index.m3u8", ".m3u8")
    
    m3u_content = (
        '#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" '
        'group-title="{group}" http-user-agent="VAVOO/1.0" http-referrer="https://vavoo.to/",{name}\n'
        '#EXTVLCOPT:http-user-agent=VAVOO/1.0\n'
        '#EXTVLCOPT:http-referrer=https://vavoo.to/\n'
        '#KODIPROP:http-user-agent=VAVOO/1.0\n'
        '#KODIPROP:http-referrer=https://vavoo.to/\n'
        '#EXTHTTP:{{"User-Agent":"VAVOO/1.0","Referer":"https://vavoo.to/"}}\n'
        '{url}'
    ).format(group=group, name=name, logo=logo, tvg_id=tvg_id, url=url)
    return m3u_content, group, url

def fetch_json_data():
    url = "https://www2.vavoo.to/live2/index?countries=all&output=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def process_item(item):
    return generate_m3u(item.get("group", ""), item.get("name", ""), item.get("logo", ""), item.get("tvg_id", ""), item.get("url", ""))

def main():
    output_dir = "/tmp/VavooGen"
    
    # Creazione della directory /tmp/VavooGen
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    index_m3u_path = os.path.join(output_dir, "index.m3u")
    ids_txt_path = os.path.join(output_dir, "ids.txt")
    html_path = os.path.join(output_dir, "index.html")
    
    try:
        json_data = fetch_json_data()
    except Exception as e:
        print("Errore nel recupero dei dati JSON:", e)
        return
    
    # Rimuovi il file `index.m3u` esistente
    if os.path.exists(index_m3u_path):
        os.remove(index_m3u_path)
    
    index_m3u = open(index_m3u_path, "w")
    index_m3u.write("#EXTM3U\n")

    groups = {}
    ids_content = ""
    processed_count = 0

    for item in json_data:
        try:
            m3u_content, group, htaccess_url = process_item(item)
        except Exception as e:
            print("Errore durante l'elaborazione di un elemento:", e)
            continue
        
        # Scrivi nei file di gruppo
        if group not in groups:
            group_file_name = os.path.join(output_dir, "index_" + group + ".m3u")
            groups[group] = open(group_file_name, "w")
            groups[group].write("#EXTM3U\n")
        
        index_m3u.write(m3u_content + "\n")
        groups[group].write(m3u_content + "\n")
        
        # Aggiorna ids.txt
        id = item["url"].replace("https://vavoo.to/live2/play/", "").replace(".ts", "")
        ids_content += id + "\n"
        processed_count += 1
        print("Canale elaborato: {}/{}".format(processed_count, len(json_data)))

    # Chiudi i file di gruppo
    for group_file in groups.values():
        group_file.close()
    
    index_m3u.close()

    # Scrivi il file ids.txt
    with open(ids_txt_path, "w") as ids_file:
        ids_file.write(ids_content)
    
    # Genera il file HTML
    html_content = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>M3U Playlists</title>\n</head>\n<body>\n'
        '<h1>M3U Playlists</h1>\n<h2><a href="index.m3u">Complete Playlist</a></h2>\n'
        '<h2>Group-specific Playlists:</h2>\n<ul>\n'
    )
    
    for group in groups.keys():
        html_content += '<li><a href="index_{}.m3u">{}</a></li>\n'.format(group, group)
    
    html_content += '</ul>\n</body>\n</html>'
    
    with open(html_path, "w") as html_file:
        html_file.write(html_content)
    
    print("File generati con successo nella directory:", output_dir)

if __name__ == "__main__":
    main()

