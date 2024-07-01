# Text+
Code Release zum Vortrag "Automatische Transkription von Podcastfolgen für Korpuslinguistische Untersuchungen."
Slides: https://zenodo.org/doi/10.5281/zenodo.12584114

- Veronika Sahlbach (https://tu-dresden.de/gsw/slk/germanistik/gls/die-professur/team-1/veronika-sahlbach)
- Vasco Alexander Sahlbach @notaTeapot

Skripte für die Whisper Automatisierung auf HPC-Sytemen: https://github.com/notaTeapot/whisper-hpc-automation


# Whisper Annotation Tools

Whisper Annotation Tools (WAT) is a set of utilities transforming whisper ASR and pyannote.speaker-diarization into transcript formats ready for further linguistic analysis.

Currently supporting:
- insanely-fast-whisper json format as input (https://github.com/Vaibhavs10/insanely-fast-whisper)
- structured output as xml or json for usage with corpus building tools (e.g. sketchengine)
- .lfk output to use with FOLKeR (https://github.com/Exmaralda-Org/exmaralda)
## Installation
```
pip install git+https://github.com/notaTeapot/whisper-annotation-tools.git
```
## Usage
```ps
usage: whisper-annotation-tools.exe [-h] --file-name FILE_NAME --output-name OUTPUT_NAME [--prepend-time PREPEND_TIME] [--metadata-file METADATA_FILE] [--audio-file AUDIO_FILE]

Whisper Annotation Tools

options:
  -h, --help            show this help message and exit
  --file-name FILE_NAME
                        Path to the whisper output json
  --output-name OUTPUT_NAME
                        Path to the desired output file, Mode defined by file extension (.flk-->FOLKER Compatible, .xml-->Corpus Tools, .json)
  --prepend-time PREPEND_TIME
                        cut off time from beginning of whisper output
  --metadata-file METADATA_FILE
                        Path to json file containing episode.
  --audio-file AUDIO_FILE
                        Path to episode audio file, used for .flk.
```
