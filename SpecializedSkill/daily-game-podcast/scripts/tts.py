#!/usr/bin/env python3
"""Call xAI TTS API to convert text to speech. Reads text from stdin or --file, writes MP3 to --output.

Requires: XAI_API_KEY environment variable.
Usage:
  python tts.py --file script.txt --output podcast.mp3
  echo "你好世界" | python tts.py --output hello.mp3 --voice ara
"""

import argparse
import os
import sys
import requests

API_URL = "https://api.x.ai/v1/tts"
VOICES = ["eve", "ara", "rex", "sal", "leo"]


def main():
    parser = argparse.ArgumentParser(description="xAI TTS - text to speech")
    parser.add_argument("--file", help="Read text from file instead of stdin")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--voice", default="rex", choices=VOICES, help="Voice ID (default: rex)")
    parser.add_argument("--language", default="zh", help="BCP-47 language code (default: zh)")
    args = parser.parse_args()

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    text = text.strip()
    if not text:
        print("Error: empty text input", file=sys.stderr)
        sys.exit(1)

    if len(text) > 15000:
        print(f"Warning: text is {len(text)} chars, TTS limit is 15000. Truncating.", file=sys.stderr)
        text = text[:14900]

    print(f"TTS: {len(text)} chars, voice={args.voice}, lang={args.language}", file=sys.stderr)

    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "voice_id": args.voice,
            "language": args.language,
            "output_format": {"codec": "mp3", "sample_rate": 44100, "bit_rate": 192000},
        },
        timeout=120,
    )

    if not resp.ok:
        print(f"TTS API error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "wb") as f:
        f.write(resp.content)

    print(f"Saved {len(resp.content):,} bytes to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
