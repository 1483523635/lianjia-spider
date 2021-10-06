import json
import sys
import os



def load_data_from_file():
    data = []
    with open("url.json", "r", encoding="utf-8") as f:
        str = f.read()
        data = json.loads(str)
    # print(data)
    return data


def flatten(t):
    return [item for sublist in t for item in sublist]


def main():
    data = load_data_from_file()
    for url in data:
        print(url.format(""))


def beep():
    os.system('say "error happened."')


if __name__ == '__main__':
    beep()
    # main()
