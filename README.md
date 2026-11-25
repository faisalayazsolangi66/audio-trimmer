# Audio Trimmer

Trim an audio file to a start/end time using ffmpeg. The cut is a fast stream copy by default; use `--reencode` for sample-exact cuts.

## Requirements

- Python 3 (standard library only — no `requirements.txt`)
- ffmpeg installed and on PATH (`sudo apt install ffmpeg` on Ubuntu/Debian, `brew install ffmpeg` on macOS)

If ffmpeg is missing, the tool exits with a clear message instead of failing mid-way.

## How to run

```bash
python3 main.py --help
python3 main.py song.mp3 --start 30 --end 1:30 --output clip.mp3
```

Options:

- `--start` — start time in seconds or `MM:SS` (default: `0`)
- `--end` — end time in seconds or `MM:SS` (default: end of file)
- `--output` — output file (default: `<name>_trimmed.<ext>`)
- `--reencode` — re-encode instead of stream-copying

## Example

```bash
$ python3 main.py song.mp3 --start 30 --end 1:30 --output clip.mp3
Trimming song.mp3 from 00:30.00 to 01:30.00 -> clip.mp3
Saved clip.mp3 (1024.0 KB).
```
