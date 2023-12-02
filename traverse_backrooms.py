import json
import random
import requests

def integer_to_roman(num):
    symbols = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]

    roman = ''
    for value, symbol in symbols:
        while num >= value:
            roman += symbol
            num -= value

    return roman

def ollama_generate(prompt, model="orca-mini", stop_token="##"):
    payload = {
        "model": model,
        "prompt": prompt,
        "raw": True,
        "stream": False,
        "options": {
            "stop": [stop_token]
        }
    }
    ollama_api = "http://localhost:11434/api/generate"
    response = requests.post(ollama_api, json=payload)
    results = response.json()
    return results["response"]


levels = {}

with open('backrooms_levels.jsonl', 'r') as f:
    for line in f:
        level = json.loads(line)
        levels[level['title']] = level

story = ""

intro = """
# THE BACKROOMS CHRONICLES

*compiled by: Anonymous*

## Prologue

>If you're not careful and you noclip out of reality in the wrong areas, you'll end up in the Backrooms, where it's nothing but the stink of old moist carpet, the madness of mono-yellow, the endless background noise of fluorescent lights at maximum hum-buzz, and approximately six hundred million square miles of randomly segmented empty rooms to be trapped in
>God save you if you hear something wandering around nearby, because it sure as hell has heard you

"""
print(intro)
story += intro

part = 1
while len(story.split())<50000:
    part_roman = integer_to_roman(part)
    part_string = f"\n\n## Part {part_roman}\n\n"
    print(part_string)
    story += part_string
    report = "MISSING PERSON REPORT\n\nName:\n"
    while True:
        character_name = ollama_generate(report, stop_token="\n")
        if character_name:
            break
    report += character_name + "\n\nLast seen: "
    while True:
        last_seen = ollama_generate(report, stop_token="\n\n")
        if last_seen:
            break
    report += last_seen + "\n\nDescription: "
    while True:
        character_description = ollama_generate(report, stop_token="\n\n")
        if character_description:
            break
    report += character_description + "\n\n"
    story += "\n```\n" + report + "\n```\n"
    print(report)
    current_level = levels['Level 0']
    chapter_no = 1
    chapter_line = f"### Part {part_roman}, Chapter 1: Level 0\n\n"

    while True:
        print(chapter_line)
        story += chapter_line
        prompt = current_level['text'] + "\n\n---\n\n" + report + "\n\n---\n\n"
        exits = [exit for exit in current_level['exits'] if exit['level'] in levels.keys()]
        if not exits:
            prompt += f"\n\n---\n\nThe following message was received from {character_name} while they were wandering {current_level['title']}. No further communications have been received since.\n\n---\n\n"
            chapter = ollama_generate(prompt)
            story += chapter
            break
        else:
            exit = random.choice(exits)
            prompt += f"\n\n---\n\nThe following message was received from {character_name} while they were wandering {current_level['title']}. It describes their experiences up until they exited to {exit['level']}.\n\n---\n\n"
            chapter = ollama_generate(prompt)
            story += chapter
            chapter_no += 1
            current_level = levels[exit['level']]
            chapter_line = f"\n\n### Part {part_roman}, Chapter {chapter_no}: {current_level['title']}\n\n"
    part += 1
    with open('the_backrooms_chronicles.md', 'w') as f:
        f.write(story)
