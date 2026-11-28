"""
화학명 TTS 음성 생성 스크립트 (무료 · API 키 불필요)

사용법
  pip install edge-tts
  python make_tts.py                      # 기본: 미국 여성 음성(Aria), 100개
  python make_tts.py --voice en-US-GuyNeural
  python make_tts.py --voices en-US-AriaNeural,en-US-GuyNeural   # 화자 여러 명
  python make_tts.py --engine gtts        # edge-tts가 안 될 때 (pip install gTTS)
  python make_tts.py --wav                # ffmpeg 있으면 16kHz mono WAV도 같이 생성

출력
  audio/<audio_id>[_<voice>].mp3 (+ .wav)
  manifest.csv  → audio_path, reference_text(정답), voice ... (ASR 결과 붙여서 WER 계산용)
"""
import argparse, asyncio, csv, os, shutil, subprocess, sys

def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="tts_sample_100.csv")
    p.add_argument("--out", default="audio")
    p.add_argument("--engine", choices=["edge", "gtts"], default="edge")
    p.add_argument("--voice", default="en-US-AriaNeural")
    p.add_argument("--voices", default="", help="쉼표로 여러 화자 지정 (voice보다 우선)")
    p.add_argument("--rate", default="+0%", help="edge-tts 말하기 속도, 예: -10%%")
    p.add_argument("--text-col", default="tts_input_text",
                   help="TTS에 넣을 열 (원문 그대로 읽히려면 reference_text)")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--wav", action="store_true")
    return p.parse_args()

async def edge_one(text, voice, rate, path):
    import edge_tts
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            if os.path.getsize(path) > 0:
                return
        except Exception as e:
            err = e
        await asyncio.sleep(2)
    raise RuntimeError(f"edge-tts 실패: {text} ({err})")

def gtts_one(text, path):
    from gtts import gTTS
    gTTS(text, lang="en", tld="com").save(path)

def to_wav(mp3, wav):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3,
                    "-ar", "16000", "-ac", "1", wav], check=True)

async def main():
    a = parse()
    rows = list(csv.DictReader(open(a.input, encoding="utf-8-sig")))
    if a.limit:
        rows = rows[: a.limit]
    voices = [v.strip() for v in a.voices.split(",") if v.strip()] or [a.voice]
    if a.engine == "gtts":
        voices = ["gtts"]
    os.makedirs(a.out, exist_ok=True)
    if a.wav and not shutil.which("ffmpeg"):
        print("ffmpeg가 없어 WAV 변환은 건너뜁니다 (mp3만 생성).")
        a.wav = False

    manifest = []
    total = len(rows) * len(voices)
    n = 0
    for v in voices:
        tag = "" if len(voices) == 1 else "_" + v.replace("en-", "").replace("Neural", "")
        for r in rows:
            n += 1
            mp3 = os.path.join(a.out, f"{r['audio_id']}{tag}.mp3")
            text = r[a.text_col]
            if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):  # 이어서 실행 가능
                if a.engine == "edge":
                    await edge_one(text, v, a.rate, mp3)
                else:
                    gtts_one(text, mp3)
            path = mp3
            if a.wav:
                path = mp3[:-4] + ".wav"
                to_wav(mp3, path)
            manifest.append({"audio_path": path, "audio_id": r["audio_id"], "voice": v,
                             "reference_text": r["reference_text"], "tts_input_text": text,
                             "class": r["class"], "molecular_formula": r["molecular_formula"]})
            print(f"[{n}/{total}] {os.path.basename(path)}  ←  {text}")

    with open("manifest.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()) + ["asr_output"])
        w.writeheader()
        for m in manifest:
            w.writerow({**m, "asr_output": ""})
    print(f"\n완료: {len(manifest)}개 → {a.out}/ , manifest.csv")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
