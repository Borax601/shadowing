"""
タイムスタンプ生成スクリプト
使い方:
  python3 generate_timestamps.py 1    → Day 1
  python3 generate_timestamps.py 1.5  → Day 1.5
"""
import sys
import json
import re
import whisper

# ── デイごとの設定 ──────────────────────────────────────────────────────────
DAY_CONFIG = {
    "1": {
        "audio":  "audio/day1.mp3",
        "output": "audio/day1_timestamps.json",
        "english": (
            "So sometimes / I get invited / to give weird talks. //"
            "I got invited / to speak / to the people / who dress up / in big stuffed animal costumes "
            "/ to perform / at sporting events. //"
            "Unfortunately / I couldn't go. //"
            "But it got me thinking / about the fact / that these guys, / at least most of them, "
            "/ know what it is / that they do for a living. //"
            "What they do is / they dress up as stuffed animals / and entertain people "
            "/ at sporting events."
        ),
    },
    "1.5": {
        "audio":  "audio/day1_5.mp3",
        "output": "audio/day1_5_timestamps.json",
        "english": (
            "Shortly after that / I got invited / to speak / at the convention / of the people "
            "/ who make balloon animals. //"
            "And again, / I couldn't go. //"
            "But it's a fascinating group. //"
            "They make balloon animals. //"
            "There is a big schism / between the ones / who make gospel animals "
            "/ and porn animals, / but -- (Laughter) / they do a lot of really cool stuff "
            "/ with balloons. //"
            "Sometimes they get in trouble, / but not often. //"
            "And the other thing / about these guys is, / they also know "
            "/ what they do for a living. //"
            "They make balloon animals."
        ),
    },
}


def clean(text):
    return re.sub(r"[^a-z0-9']", "", text.lower())


def build_segments(english_text):
    raw = re.split(r"\s*//?\s*", english_text)
    return [s.strip() for s in raw if s.strip()]


def align_segments(segments, words):
    result = []
    word_idx = 0
    total_words = len(words)

    for seg_idx, seg in enumerate(segments):
        seg_words = seg.split()
        seg_cleaned = [clean(w) for w in seg_words]

        start_time = None
        end_time = None
        matched = 0
        candidate_start = word_idx
        candidate_start_time = None

        search_end = min(word_idx + len(seg_cleaned) * 3 + 10, total_words)

        for i in range(word_idx, search_end):
            if i >= total_words:
                break
            w_clean = clean(words[i]["word"])
            if not w_clean:
                continue
            if w_clean == seg_cleaned[matched]:
                if matched == 0:
                    candidate_start = i
                    candidate_start_time = words[i]["start"]
                matched += 1
                if matched == len(seg_cleaned):
                    start_time = candidate_start_time
                    end_time = words[i]["end"]
                    word_idx = i + 1
                    break
            else:
                matched = 0

        if start_time is None:
            start_time = result[-1]["end"] if result else 0.0
            end_time = start_time + 1.0
            print(f"  [WARNING] segment {seg_idx}: '{seg}'")
        else:
            print(f"  [OK] segment {seg_idx}: '{seg[:45]}' {start_time:.2f}s - {end_time:.2f}s")

        result.append({
            "index": seg_idx,
            "text": seg,
            "start": round(start_time, 3),
            "end":   round(end_time, 3),
        })

    return result


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else "1"
    if day not in DAY_CONFIG:
        print(f"エラー: 未対応のデイ '{day}'. 対応: {list(DAY_CONFIG.keys())}")
        sys.exit(1)

    cfg = DAY_CONFIG[day]
    print(f"=== Day {day} タイムスタンプ生成 ===")
    print(f"音声: {cfg['audio']}")
    print(f"出力: {cfg['output']}")
    print()

    print("Whisper medium モデルをロード中...")
    model = whisper.load_model("medium")

    print(f"文字起こし中: {cfg['audio']}")
    result = model.transcribe(cfg["audio"], word_timestamps=True, language="en")

    all_words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            all_words.append({
                "word":  w["word"].strip(),
                "start": w["start"],
                "end":   w["end"],
            })
    print(f"Whisper 単語数: {len(all_words)}")

    segments = build_segments(cfg["english"])
    print(f"セグメント数: {len(segments)}")
    print()
    print("セグメントをアライン中...")

    aligned = align_segments(segments, all_words)

    with open(cfg["output"], "w", encoding="utf-8") as f:
        json.dump(aligned, f, ensure_ascii=False, indent=2)

    print(f"\n完了: {cfg['output']} に {len(aligned)} セグメント保存しました")


if __name__ == "__main__":
    main()
