import json
import argparse
from .main import annotate_episode

parser = argparse.ArgumentParser(description="Whisper Annotation Tools")
parser.add_argument(
    "--file-name", required=True, type=str, help="Path to the whisper output json"
)

parser.add_argument(
    "--output-name",
    required=True,
    type=str,
    help="Path to the desired output file, Mode defined by file extension (.flk-->FOLKER Compatible, .xml-->Corpus Tools, .json)",
)

parser.add_argument(
    "--prepend-time",
    required=False,
    type=float,
    default=0,
    help="cut off time from beginning of whisper output",
)

parser.add_argument(
    "--metadata-file",
    required=False,
    type=str,
    default=None,
    help="Path to json file containing episode.",
)
parser.add_argument(
    "--audio-file",
    required=False,
    type=str,
    default="",
    help="Path to episode audio file, used for .flk.",
)


def main():
    args = parser.parse_args()

    with open(args.file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.metadata_file is not None:
        with open(args.metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        metadata = None

    annotate_episode(
        data, args.output_name, args.prepend_time, metadata, args.audio_file
    )
