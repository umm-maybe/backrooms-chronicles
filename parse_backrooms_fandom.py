import csv
jsonl_file = open("backrooms_levels.jsonl", "w")
import re
import json
from bs4 import BeautifulSoup
from wikitextparser import remove_markup, parse
with open("backrooms_pages_current.xml", "r") as xml_doc:
    xml_doc = xml_doc.read()
    soup = BeautifulSoup(xml_doc, 'xml')
    for page in soup.find_all('page'):
        # get child tag named "title" for each page
        title = page.find('title').contents[0].get_text()
        if title.find("Level") != 0:
            continue
        if title.find("Level List") == 0:
            continue
        print(title)
        revision = page.find('revision')
        try:
            author = revision.find('contributor').find('username').contents[0]
        except Exception as e:
            print(e)
        # get child tag named "text" for each revision
        html_as_text = revision.find('text').contents[0].get_text()
        spoonful = BeautifulSoup(html_as_text, 'html.parser')
        actual_text = spoonful.get_text().encode('ascii', 'ignore').decode()
        #actual_text = re.sub(r"\{\{.*?\}\}","",actual_text, re.DOTALL)
        #actual_text = re.sub(r"File:([^\\\n]*)","",actual_text, re.DOTALL)
        #actual_text = re.sub(r"__.*?__","",actual_text, re.DOTALL)
        #actual_text = re.sub(r"\[\[[^\]]*?:[^\]]*?\]\]","",actual_text, re.DOTALL)
        #actual_text = actual_text.replace("'''","")
        #actual_text = actual_text.replace('\"','"')
        #actual_text = actual_text.split("Open Author")[0]
        entrances = []
        exits = []
        heading = ""
        for line in actual_text.split("\n"):
            match1 = re.search("=+(.*?)=+",line)
            if match1:
                heading = match1.group(1).strip()
                print("\t"+heading)
            if heading in ["Entrances","Exits"]:
                match2 = re.search("\[\[(.*?)\]\]",line)
                if match2:
                    print("\t\t"+match2.group(1))
                    sentences = re.split(r'(?<=[.!?]) +', line)
                    sentence = re.sub("\[\[(.*?)\]\]",r'\1',sentences[0])
                    if "Entrances" in heading:
                        entrances.append({"level": match2.group(1), "description": sentence})
                    elif "Exits" in heading:
                        exits.append({"level": match2.group(1), "description": sentence})
        actual_text = parse(actual_text).plain_text()
        jsonl_file.write(json.dumps({"author":author,"title":title,"text":actual_text,"entrances":entrances,"exits":exits}))
        jsonl_file.write("\n")
jsonl_file.close()
