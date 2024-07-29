import json
from .utils.structure import structure_whisper_speakers, build_xml, build_flk


def annotate_episode(
    data: dict,
    output_name: str,
    prepend_time: float = 0,
    metadata: dict = None,
    audio_filename="",
    mark_pauses=False,
    min_pause=0.1,
):
    structured_data = structure_whisper_speakers(
        data, prepend_time, mark_pauses, min_pause
    )

    if output_name.endswith(".json"):
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)

    elif output_name.endswith(".xml"):
        build_xml(output_name, structured_data, metadata)

    elif output_name.endswith(".flk"):
        if not audio_filename.endswith(".wav"):
            print("Audio Filetype not supported in .flk format! Use .wav instead.")

        build_flk(output_name, structured_data, audio_filename, metadata)
