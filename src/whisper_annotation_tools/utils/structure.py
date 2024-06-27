import json
import xml.etree.ElementTree as ET
import os
import datetime


def _indent_xml(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def _timestamp_to_h(timestamp_s):
    hours = int(timestamp_s // 3600)
    minutes = int((timestamp_s % 3600) // 60)
    timestamp_s = timestamp_s % 60
    return f"{hours:02}:{minutes:02}:{timestamp_s:02.0f}"


def prepend_time(time: float):
    raise NotImplementedError


def structure_whisper_chunks():
    raise NotImplementedError


def structure_whisper_speakers(data: dict, prepend_time: float = 0) -> dict:
    """Structure whisper speaker aligned chunks into sentences and speaker aligned paragraphs.

    Parameters
    ----------
    data : dict
        data containing the speaker aligned segments in the key "speakers"

    Returns
    -------
    dict
        structured data
    Raises
    ------
    KeyError
        Fails if no data speaker chunks not in data
    """
    if "speakers" not in data.keys():
        raise KeyError("Failed to structure whisper data, no speaker segments found!")
    speakers = data["speakers"]

    # delete chunks from beginning and subtract timestamp
    new_speakers = []
    for element in speakers:
        element["timestamp_h"] = ["none", "none"]
        if isinstance(element["timestamp"][0], float):
            element["timestamp"][0] = round(element["timestamp"][0] - prepend_time, 2)
            element["timestamp_h"][0] = _timestamp_to_h(element["timestamp"][0])
        if isinstance(element["timestamp"][1], float):
            element["timestamp"][1] = round(element["timestamp"][1] - prepend_time, 2)
            element["timestamp_h"][1] = _timestamp_to_h(element["timestamp"][1])

        if element["timestamp"][0] >= 0:
            new_speakers.append(element)

    speakers = new_speakers

    last_speaker = None
    last_ts = [0, 0]

    sentence_start = None
    sentence_stop = None
    sentence_start_h = None
    sentence_stop_h = None

    document = []
    paragraph_sentences = []
    sentence_text = ""

    for element in speakers:
        speaker = element["speaker"]
        if sentence_text == "":
            sentence_start = element["timestamp"][0]
            sentence_start_h = element["timestamp_h"][0]

        if speaker != last_speaker and len(paragraph_sentences) != 0:
            paragraph = {
                "speaker": last_speaker,
                "timestamp": [
                    paragraph_sentences[0]["timestamp"][0],
                    paragraph_sentences[-1]["timestamp"][1],
                ],
                "timestamp_h": [
                    paragraph_sentences[0]["timestamp_h"][0],
                    paragraph_sentences[-1]["timestamp_h"][1],
                ],
                "sentences": paragraph_sentences,
            }
            document.append(paragraph)

            # reset current paragraph
            paragraph_sentences = []

        # extend current sentence
        sentence_stop = element["timestamp"][1]
        sentence_stop_h = element["timestamp_h"][1]
        sentence_text += element["text"]

        # error in here
        if element["text"][-1] in [".", "?", "!"]:
            # end of sentence
            sentence = {
                "text": sentence_text[1:],
                "timestamp": [sentence_start, sentence_stop],
                "timestamp_h": [sentence_start_h, sentence_stop_h],
            }
            # add sentence to paragraph reset text
            paragraph_sentences.append(sentence)
            sentence_text = ""
        # reset last speaker
        last_speaker = speaker

    try:
        paragraph = {
            "speaker": last_speaker,
            "timestamp": [
                paragraph_sentences[0]["timestamp"][0],
                paragraph_sentences[-1]["timestamp"][1],
            ],
            "timestamp_h": [
                paragraph_sentences[0]["timestamp_h"][0],
                paragraph_sentences[-1]["timestamp_h"][1],
            ],
            "sentences": paragraph_sentences,
        }
        document.append(paragraph)
    except:
        pass

    return document


def build_flk(filename, document, audio_filename, metadata=None):
    doc = ET.Element("folker-transcription")

    # Build document head with transcription log
    head = ET.SubElement(doc, "head")
    current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    transcription_log = ET.SubElement(head, "transcription-log")
    log_entry = ET.SubElement(
        transcription_log,
        "log-entry",
        {"start": current_time, "end": current_time, "who": "system"},
    )

    if metadata is None:
        log_entry.text = f"Generated by whisper-annotation-tools"
    else:
        log_entry.text = f"Generated by whisper-annotation-tools {metadata['name']}, {metadata['date']}, {metadata['spotify_url']}"

    # Create placeholders for readability
    speakers = ET.SubElement(doc, "speakers")
    recording = ET.SubElement(doc, "recording", {"path": audio_filename})
    timeline = ET.SubElement(doc, "timeline")

    # Structure sentences
    speakers_list = []
    start_ts = 0
    end_ts = 0
    start_id = 0
    end_id = 0
    last_id = 0
    for paragraph in document:
        if paragraph["speaker"] not in speakers_list:
            speakers_list.append(paragraph["speaker"])

        for sentence in paragraph["sentences"]:
            if sentence["timestamp"][0] != start_ts:
                last_id += 1
                start_id = last_id
                start_ts = sentence["timestamp"][0]
                t_attrib = {
                    "timepoint-id": f"TLI_{start_id}",
                    "absolute-time": f"{start_ts}",
                }
                t = ET.SubElement(timeline, "timepoint", t_attrib)
            if sentence["timestamp"][1] != end_ts:
                last_id += 1
                end_id = last_id
                end_ts = sentence["timestamp"][1]
                t_attrib = {
                    "timepoint-id": f"TLI_{end_id}",
                    "absolute-time": f"{end_ts}",
                }
                t = ET.SubElement(timeline, "timepoint", t_attrib)

            contrib_attrib = {
                "speaker-reference": paragraph["speaker"],
                "start-reference": f"TLI_{start_id}",
                "end-reference": f"TLI_{end_id}",
            }
            c = ET.SubElement(doc, "contribution", contrib_attrib)
            u = ET.SubElement(c, "unparsed")
            u.text = sentence["text"]

    # Populate speaker list
    speakers_list.sort()
    for speaker in speakers_list:
        s_attrib = {"speaker-id": speaker}
        s = ET.SubElement(speakers, "speaker", s_attrib)
        s_n = ET.SubElement(s, "name")
        s_n.text = speaker

    # Format and save
    _indent_xml(doc)
    tree = ET.ElementTree(doc)

    tree.write(filename, encoding="utf-8", xml_declaration=True)


def build_xml(filename, document, metadata=None):
    if metadata is None:
        doc = ET.Element("doc", {"filename": filename})
    else:
        doc = ET.Element("doc", metadata)
    comment = ET.Comment("Generated by whisper-annotation-tools")
    doc.append(comment)

    for paragraph in document:
        # print(paragraph)
        attrib = {
            key: value
            for key, value in paragraph.items()
            if key in ["speaker", "timestamp", "timestamp_h"]
        }
        p = ET.SubElement(doc, "p", attrib)
        for sentence in paragraph["sentences"]:
            attrib = {
                key: value
                for key, value in sentence.items()
                if key in ["timestamp", "timestamp_h"]
            }
            s = ET.SubElement(p, "s", attrib)
            s.text = sentence["text"]

    _indent_xml(doc)
    tree = ET.ElementTree(doc)

    tree.write(filename, encoding="utf-8", xml_declaration=True)
