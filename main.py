#!/usr/bin/env python3
"""Trim an audio file to a start/end time using ffmpeg.

ffmpeg must be installed and on PATH. The tool checks for it first
and exits with a clear message if it is missing, before touching
any files.
"""
import argparse
import os
import shutil
import subprocess
import sys


def parse_time(text):
    """Accept seconds (90, 90.5) or MM:SS / HH:MM:SS."""
    parts = text.split(":")
    try:
        values = [float(part) for part in parts]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid time {text!r}: use seconds or MM:SS"
        )
    if len(values) == 1:
        total = values[0]
    elif len(values) == 2:
        total = values[0] * 60 + values[1]
    elif len(values) == 3:
        total = values[0] * 3600 + values[1] * 60 + values[2]
    else:
        raise argparse.ArgumentTypeError(
            f"invalid time {text!r}: use seconds or MM:SS"
        )
    if total < 0:
        raise argparse.ArgumentTypeError("time must not be negative")
    return total


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
    return f"{minutes:02d}:{secs:05.2f}"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Trim an audio file to a start/end time using ffmpeg."
    )
    parser.add_argument("input", help="input audio file (mp3, wav, m4a, ...)")
    parser.add_argument("--start", type=parse_time, default=0.0,
                        help="start time in seconds or MM:SS (default: 0)")
    parser.add_argument("--end", type=parse_time, default=None,
                        help="end time in seconds or MM:SS (default: end of file)")
    parser.add_argument("--output", default=None,
                        help="output file (default: <name>_trimmed.<ext>)")
    parser.add_argument("--reencode", action="store_true",
                        help="re-encode instead of stream-copying (slower, exact cuts)")
    args = parser.parse_args(argv)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("Error: ffmpeg is not installed or not on PATH.", file=sys.stderr)
        print("Install ffmpeg first, then run this tool again.", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt install ffmpeg", file=sys.stderr)
        print("  macOS:         brew install ffmpeg", file=sys.stderr)
        print("  Windows:       winget install ffmpeg", file=sys.stderr)
        return 1

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1
    if args.end is not None and args.end <= args.start:
        print("Error: --end must be after --start.", file=sys.stderr)
        return 1

    if args.output:
        output = args.output
    else:
        stem, ext = os.path.splitext(args.input)
        output = f"{stem}_trimmed{ext or '.mp3'}"
    if os.path.abspath(output) == os.path.abspath(args.input):
        print("Error: output must be different from the input file.",
              file=sys.stderr)
        return 1

    cmd = [ffmpeg, "-y", "-ss", str(args.start), "-i", args.input]
    if args.end is not None:
        cmd += ["-to", str(args.end)]
    if not args.reencode:
        cmd += ["-c", "copy"]
    cmd.append(output)

    print(f"Trimming {args.input} from {format_time(args.start)}"
          + (f" to {format_time(args.end)}" if args.end is not None else " to end")
          + f" -> {output}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg failed:", file=sys.stderr)
        tail = (result.stderr or "").strip().splitlines()[-5:]
        print("\n".join(tail), file=sys.stderr)
        return 1

    size_kb = os.path.getsize(output) / 1024
    print(f"Saved {output} ({size_kb:.1f} KB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
