import json
import os
import analyzer
import argparse
import whisper
import openai


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="inventory app")
    parser.add_argument('-t', '--test', action='store_true', required=False, help='text input')

    args = parser.parse_args()
    test = args.test

    if test:
        analyzer.get_transcript("/Users/willjackson/git/inventory_app/audio1091256847.m4a","/Users/willjackson/git/inventory_app/audio1091256847.m4a")
        exit()


