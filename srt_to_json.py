import json
import os


def timecode_to_seconds(tc: str) -> float:
    h, m, s_ms = tc.split(":")
    if "," in s_ms:
        s, ms = s_ms.split(",")
    else:
        s, ms = s_ms.split(".")
    return (int(h)*60*60) + (int(m)*60) + int(s) + int(ms)/1000


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


for srt in os.listdir("transcripts"):
    filename, ext = os.path.splitext(srt)
    srt_file = os.path.join("transcripts", srt)
    json_file = os.path.join("transcripts", filename + ".json")

    if ext != ".srt" or os.path.exists(json_file):
        continue

    with open(srt_file, "r", encoding="utf-8") as f:
        data = f.readlines()

    segments = []
    current_block = {}
    for chunk in chunker(data, 4):
        if len(chunk) != 4:
            break

        # add id
        current_block["id"] = int(chunk[0].strip())

        # add timecodes
        tc_start, tc_end = chunk[1].strip().split(" --> ")
        current_block["start"] = timecode_to_seconds(tc_start)
        current_block["end"] = timecode_to_seconds(tc_end)

        # add text
        current_block["text"] = chunk[2].strip()

        # append and cleanup
        segments.append(current_block)
        current_block = {}

    final_json = {
        "text": "",
        "segments": segments
    }

    for i in segments:
        try:
            final_json["text"] += i["text"]
        except:
            print(i)
            print(srt)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(final_json, f)
