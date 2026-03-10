#!/usr/bin/env python3
"""
Transcribe audio using faster-whisper (falls back to openai-whisper if unavailable).

Usage:
    python3 transcribe.py <audio_file> --model <model> --language <lang> --output <output_txt>

Output format (one segment per line):
    [START_SEC] TEXT

Example:
    python3 transcribe.py /tmp/podcast_abc123.m4a --model medium --language zh --output /tmp/transcript_abc123.txt
"""

import sys
import argparse


def transcribe_faster_whisper(audio_file, model, language, output_file):
    from faster_whisper import WhisperModel
    print(f"Backend: faster-whisper | Model: {model} | Language: {language}", flush=True)
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = m.transcribe(audio_file, language=language, beam_size=5)
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in segments:
            line = f"[{seg.start:.1f}s] {seg.text.strip()}"
            f.write(line + "\n")
            print(line, flush=True)


def transcribe_whisper(audio_file, model, language, output_file):
    import whisper
    print(f"Backend: openai-whisper | Model: {model} | Language: {language}", flush=True)
    m = whisper.load_model(model)
    result = m.transcribe(audio_file, language=language, fp16=False)
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            line = f"[{seg['start']:.1f}s] {seg['text'].strip()}"
            f.write(line + "\n")
            print(line, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file")
    parser.add_argument("--model", default="medium")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        import faster_whisper  # noqa: F401
        has_faster_whisper = True
    except ImportError:
        has_faster_whisper = False

    try:
        import whisper  # noqa: F401
        has_whisper = True
    except ImportError:
        has_whisper = False

    if has_faster_whisper:
        transcribe_faster_whisper(args.audio_file, args.model, args.language, args.output)
    elif has_whisper:
        transcribe_whisper(args.audio_file, args.model, args.language, args.output)
    else:
        print("Error: Neither faster-whisper nor openai-whisper is installed.", file=sys.stderr)
        print("Install: pip install faster-whisper", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
