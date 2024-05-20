import datetime
import os


def main():
    files_to_redo = []
    transcripts_path = os.path.abspath("./transcripts")

    for _file in os.listdir(transcripts_path):
        if not _file.endswith(".txt"):
            continue

        abs_path = os.path.abspath(os.path.join(transcripts_path, _file))

        if check_line_repetition(abs_path):
            files_to_redo.append(abs_path)
            filename = os.path.splitext(abs_path)[0]
            os.remove(filename + ".json")
            os.remove(filename + ".srt")
            os.remove(filename + ".vtt")
            os.remove(abs_path)

    print(f"Deleted {len(files_to_redo)} transcripts to re-do")


def check_line_repetition(filename) -> bool:
    with open(filename, "r", encoding="utf-8") as file:
        previous_line = None
        i = 0

        # check for 10 lines to be the same
        for line in file:
            if line == previous_line:
                i += 1
                if i >= 10:
                    return True
            else:
                previous_line = line
                i = 1

    return False


if __name__ == "__main__":
    main()
