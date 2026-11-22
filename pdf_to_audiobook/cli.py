"""Command-line entry point. With no PDF given, opens the desktop app."""

import argparse
import sys

from .config import DEFAULT_SPEED, DEFAULT_VOICE, SPEED_MAX, SPEED_MIN, VOICES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf-to-audiobook",
        description="Convert a PDF to an MP3 audiobook, fully offline. "
                    "Run with no arguments to open the desktop app.",
    )
    p.add_argument("pdf", nargs="?", help="PDF to convert (omit to launch the GUI)")
    p.add_argument("-o", "--output", help="output file (default: next to the PDF, .mp3)")
    p.add_argument("-v", "--voice", default=DEFAULT_VOICE,
                   help=f"Kokoro voice ID (default: {DEFAULT_VOICE}); see --list-voices")
    p.add_argument("-s", "--speed", type=float, default=DEFAULT_SPEED,
                   help=f"speaking speed, {SPEED_MIN}-{SPEED_MAX} (default: {DEFAULT_SPEED})")
    p.add_argument("--list-voices", action="store_true", help="show built-in voices and exit")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_voices:
        for label, vid in VOICES.items():
            print(f"  {vid:<12} {label}")
        print("\nAny other Kokoro English voice ID (a*/b* prefix) also works.")
        return 0

    if not args.pdf:
        from .gui import run
        run()
        return 0

    if args.voice[:1] not in ("a", "b"):
        print(f"error: unsupported voice '{args.voice}' (English voices start with a or b)",
              file=sys.stderr)
        return 2
    if not SPEED_MIN <= args.speed <= SPEED_MAX:
        print(f"error: speed must be between {SPEED_MIN} and {SPEED_MAX}", file=sys.stderr)
        return 2

    from .converter import ConversionError, convert_pdf
    from .device import device_label

    print(f"Device: {device_label()}")
    try:
        out = convert_pdf(args.pdf, args.voice, args.speed, out_path=args.output,
                          on_status=lambda m: print(f"\r{m:<60}", end="", flush=True))
    except ConversionError as e:
        print(f"\nerror: {e}", file=sys.stderr)
        return 1
    print(f"\nSaved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
