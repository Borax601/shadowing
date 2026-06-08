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
    "2": {
        "audio":  "audio/day2.mp3",
        "output": "audio/day2_timestamps.json",
        "english": (
            "But what do we do / for a living? //"
            "What exactly / do the people watching this / do every day? //"
            "And I want to argue / that what we do / is we try to change everything. //"
            "That we try to find / a piece of the status quo -- "
            "/ something that bothers us, / something that needs to be improved, "
            "/ something that is itching to be changed -- / and we change it. //"
            "We try to make / big, permanent, important change. //"
            "But we don't think about it / that way."
        ),
    },
    "3": {
        "audio":  "audio/day3.mp3",
        "output": "audio/day3_timestamps.json",
        "english": (
            "First, / about a guy named Nathan Winograd. //"
            "Nathan was / the number two person / at the San Francisco SPCA. //"
            "And what you may not know / about the history of the SPCA is, "
            "/ it was founded / to kill dogs and cats. //"
            "Cities gave them a charter / to get rid of the stray animals "
            "/ on the street / and destroy them. //"
            "In a typical year / four million dogs and cats / were killed, "
            "/ most of them / within 24 hours / of being scooped off of the street."
        ),
    },
    "4": {
        "audio":  "audio/day4.mp3",
        "output": "audio/day4_timestamps.json",
        "english": (
            "Nathan and his boss saw this, / and they could not tolerate it. //"
            "So they set out / to make San Francisco / a no-kill city: "
            "/ create an entire city / where every dog and cat, "
            "/ unless it was ill or dangerous, / would be adopted, / not killed. //"
            "And everyone said / it was impossible. //"
            "Nathan and his boss / went to the city council "
            "/ to get a change in the ordinance. //"
            "And people from SPCAs / and humane shelters / around the country "
            "/ flew to San Francisco / to testify against them -- "
            "/ to say / it would hurt the movement / and it was inhumane."
        ),
    },
    "9": {
        "audio":  "audio/day9.mp3",
        "output": "audio/day9_timestamps.json",
        "english": (
            "So let me tell you / about the three cycles. //"
            "The first one is / the factory cycle. //"
            "Henry Ford / comes up with a really cool idea. //"
            "It enables him / to hire men "
            "/ who used to get paid 50 cents a day "
            "/ and pay them / five dollars a day. //"
            "Because he's got / an efficient enough factory. //"
            "Well with that sort of advantage / you can churn out / a lot of cars. //"
            "You can make a lot of change. //"
            "You can get roads built. //"
            "The essence of what you're doing / is you need "
            "/ ever-cheaper labor, / and ever-faster machines. //"
            "And the problem we've run into is, / we're running out of both."
        ),
    },
    "8": {
        "audio":  "audio/day8.mp3",
        "output": "audio/day8_timestamps.json",
        "english": (
            "We started / with the factory idea: "
            "/ that you could change the whole world "
            "/ if you had an efficient factory / that could churn out change. //"
            "We then went to the TV idea, / that said "
            "/ if you had a big enough mouthpiece, "
            "/ if you could get on TV / enough times, "
            "/ if you could buy enough ads, / you could win. //"
            "And now we're in / this new model of leadership, "
            "/ where the way we make change "
            "/ is not by using money or power / to lever a system, "
            "/ but by leading."
        ),
    },
    "7": {
        "audio":  "audio/day7.mp3",
        "output": "audio/day7_timestamps.json",
        "english": (
            "And when I think about / what Nathan did, "
            "/ and when I think about / what people here do, "
            "/ I think about ideas. //"
            "And I think about the idea / that creating an idea, "
            "/ spreading an idea / has a lot behind it. //"
            "I don't know / if you've ever been / to a Jewish wedding, "
            "/ but what they do is, / they take a light bulb / and they smash it. //"
            "Now there is a bunch of reasons / for that. //"
            "But one reason is / because it indicates a change, "
            "/ from before to after. //"
            "It is a moment in time. //"
            "And I want to argue / that we are living through "
            "/ and are right at / the key moment / of a change "
            "/ in the way ideas are created / and spread / and implemented."
        ),
    },
    "6": {
        "audio":  "audio/day6.mp3",
        "output": "audio/day6_timestamps.json",
        "english": (
            "They persisted. //"
            "And Nathan went directly / to the community. //"
            "He connected / with people who cared about this: "
            "/ nonprofessionals, / people with passion. //"
            "And within just a couple years, / San Francisco became "
            "/ the first no-kill city, / running no deficit, "
            "/ completely supported by the community. //"
            "Nathan left / and went to Tompkins County, New York -- "
            "/ a place as different from San Francisco "
            "/ as you can be / and still be in the United States. //"
            "And he did it again."
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
