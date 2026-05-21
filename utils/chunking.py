import json
import os


def load_play_files(folder_path):
    plays = []

    for filename in sorted(os.listdir(folder_path)):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "scenes" in data:
            plays.append(data)

    return plays


def format_utterance(utterance):
    speaker = utterance.get("speaker", "UNKNOWN")
    text = utterance.get("text", "").strip()

    if speaker == "STAGE_DIRECTION":
        return f"[Stage] {text}"

    return f"{speaker}: {text}"


def build_scene_header(scene, play_title):
    act = scene.get("act", "")
    scene_num = scene.get("scene", "")
    location = scene.get("location", "")

    summary = ""
    utterances = scene.get("utterances", [])
    if utterances:
        summary = utterances[0].get("scene_summary", "")

    location_part = f" | Location: {location}" if location else ""

    return (
        f"Play: {play_title} | Act {act} Scene {scene_num}{location_part}\n"
        f"Summary: {summary}\n\n"
    )


def build_chunk_metadata(scene, play_title, utterances, start_idx, end_idx):
    first = utterances[0]
    last = utterances[-1]
    speakers = sorted({u.get("speaker", "") for u in utterances if u.get("speaker")})
    keywords = first.get("keywords", [])
    keywords_str = ",".join(keywords) if isinstance(keywords, list) else str(keywords)

    return {
        "play": play_title,
        "act": int(scene.get("act", 0)),
        "scene": int(scene.get("scene", 0)),
        "scene_id": scene.get("scene_id", ""),
        "location": scene.get("location", "") or first.get("location", ""),
        "utterance_id_start": first.get("utterance_id", ""),
        "utterance_id_end": last.get("utterance_id", ""),
        "chunk_utterance_start": start_idx,
        "chunk_utterance_end": end_idx,
        "speakers": ",".join(speakers),
        "keywords": keywords_str,
    }


def chunk_scene(scene, play_title, max_tokens=450, overlap_utterances=3):
    utterances = scene.get("utterances", [])
    if not utterances:
        return []

    header = build_scene_header(scene, play_title)
    formatted_lines = [format_utterance(u) for u in utterances]
    scene_id = scene.get("scene_id", f"{play_title}_{scene.get('act')}_{scene.get('scene')}")
    header_tokens = len(header.split())
    full_text = header + "\n".join(formatted_lines)

    if len(full_text.split()) <= max_tokens:
        return [
            {
                "id": f"{scene_id}_chunk_0",
                "text": full_text,
                "metadata": build_chunk_metadata(
                    scene, play_title, utterances, 0, len(utterances) - 1
                ),
            }
        ]

    chunks = []
    start_idx = 0
    chunk_index = 0

    while start_idx < len(utterances):
        batch_lines = []
        batch_start = start_idx
        token_count = header_tokens
        i = start_idx

        while i < len(utterances):
            line = formatted_lines[i]
            line_tokens = len(line.split()) + 1

            if token_count + line_tokens > max_tokens and batch_lines:
                break

            batch_lines.append(line)
            token_count += line_tokens
            i += 1

        if not batch_lines:
            batch_lines = [formatted_lines[start_idx]]
            i = start_idx + 1

        batch_utterances = utterances[batch_start:i]
        chunk_text = header + "\n".join(batch_lines)

        chunks.append(
            {
                "id": f"{scene_id}_chunk_{chunk_index}",
                "text": chunk_text,
                "metadata": build_chunk_metadata(
                    scene, play_title, batch_utterances, batch_start, i - 1
                ),
            }
        )

        chunk_index += 1

        if i >= len(utterances):
            break

        next_start = max(batch_start + 1, i - overlap_utterances)
        start_idx = next_start if next_start > batch_start else i

    return chunks


def chunks_from_play(play_data, max_tokens=450, overlap_utterances=3):
    play_title = play_data.get("metadata", {}).get("title", "Unknown")
    all_chunks = []

    for scene in play_data.get("scenes", []):
        all_chunks.extend(
            chunk_scene(
                scene,
                play_title,
                max_tokens=max_tokens,
                overlap_utterances=overlap_utterances,
            )
        )

    return all_chunks
