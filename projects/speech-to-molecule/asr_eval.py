"""
화학명 TTS 음성 → Whisper large-v3 ASR → 오류 분석

  python asr_eval.py gen     # (음성이 없을 때) tts_1000.csv로 edge-tts 음성 재생성 (wav 16k mono)
  python asr_eval.py asr     # Whisper large-v3 (transformers, GPU 권장)로 받아쓰기 → asr_raw.csv
  python asr_eval.py score   # 채점 → asr_results_1000.csv + 요약 출력

채점 지표
  exact        : ASR 결과(소문자, 끝 마침표 제거) == 정답 IUPAC 이름
  compact      : 숫자 단어→숫자 변환 후 공백·쉼표·하이픈 제거하고 비교 (표기 차이 무시)
  cer          : compact 문자열 기준 문자 오류율
  opsin_parse  : ASR 결과를 OPSIN이 화학명으로 해석할 수 있는가
  struct_match : OPSIN(ASR 결과) 구조 == 정답 구조 (canonical SMILES 비교)  ← 핵심
  오류 유형    : locant(위치번호) / halogen(할로젠 종류·개수) / chain(주사슬 길이) / suffix(작용기 접미사)
"""
import asyncio, csv, os, re, subprocess, sys, warnings
warnings.filterwarnings("ignore")

CSV_IN = "tts_1000.csv"
AUDIO = "audio_1000"
RAW = "asr_raw.csv"
OUT = "asr_results_1000.csv"

def rows():
    return list(csv.DictReader(open(CSV_IN, encoding="utf-8-sig")))

# ---------------- 1. TTS 재생성 (병렬) ----------------
async def _gen():
    import edge_tts
    os.makedirs(AUDIO, exist_ok=True)
    sem = asyncio.Semaphore(8)
    rs = rows()
    done = 0
    async def one(r):
        nonlocal done
        wav = f"{AUDIO}/{r['audio_id']}.wav"
        if os.path.exists(wav) and os.path.getsize(wav) > 0:
            done += 1; return
        mp3 = wav[:-4] + ".mp3"
        async with sem:
            for _ in range(4):
                try:
                    await edge_tts.Communicate(r["tts_input_text"], "en-US-AriaNeural").save(mp3)
                    if os.path.getsize(mp3) > 0: break
                except Exception:
                    await asyncio.sleep(2)
        p = await asyncio.create_subprocess_exec("ffmpeg", "-y", "-loglevel", "error", "-i", mp3,
                                                 "-ar", "16000", "-ac", "1", wav)
        await p.wait()
        done += 1
        if done % 100 == 0: print(f"TTS {done}/{len(rs)}", flush=True)
    await asyncio.gather(*(one(r) for r in rs))
    print("TTS 완료", flush=True)

# ---------------- 2. ASR ----------------
def asr():
    # faster-whisper는 Colab(CUDA 13)에서 libcublas.so.12 오류 → transformers로 같은 Whisper large-v3 실행
    import torch, soundfile as sf
    from transformers import pipeline
    dev = 0 if torch.cuda.is_available() else -1
    print("device:", "cuda" if dev == 0 else "cpu", flush=True)
    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3",
                    torch_dtype=torch.float16 if dev == 0 else torch.float32, device=dev)
    rs = rows()
    with open(RAW, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["audio_id", "asr_output"])
        B = 8   # T4 16GB 기준 (16은 OOM)
        for i in range(0, len(rs), B):
            chunk = rs[i:i+B]
            auds = [{"raw": sf.read(f"{AUDIO}/{r['audio_id']}.wav", dtype="float32")[0], "sampling_rate": 16000} for r in chunk]
            outs = pipe(auds, batch_size=B, generate_kwargs={"language": "en", "task": "transcribe", "num_beams": 5, "max_new_tokens": 48})
            for r, o in zip(chunk, outs):
                w.writerow([r["audio_id"], o["text"].strip()])
            f.flush()
            if (i + B) % 96 == 0 or i + B >= len(rs): print(f"ASR {min(i+B, len(rs))}/1000", flush=True)
    print("ASR 완료", flush=True)

# ---------------- 3. 채점 ----------------
NUM = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}
NUM.update({"first": "1", "second": "2", "third": "3"})

def words2digits(s):
    s = s.lower()
    # "twenty one" 같은 경우는 화학명에 거의 없으므로 단어 단위 치환만
    return re.sub(r"\b(" + "|".join(sorted(NUM, key=len, reverse=True)) + r")\b", lambda m: NUM[m.group(1)], s)

def clean(s):
    return s.strip().strip('"').rstrip(".").strip().lower()

def compact(s):
    c = re.sub(r"[^a-z0-9]", "", words2digits(clean(s)))
    return c.replace("eicos", "icos")   # eicosane = icosane (둘 다 맞는 이름)

def locants(s):
    return re.findall(r"\d+", words2digits(clean(s)))

HAL = ["fluoro", "chloro", "bromo", "iodo"]
def halogens(s):
    c = compact(s)
    return tuple(len(re.findall(h, c)) for h in HAL)

CHAIN = ["eicos", "icos", "nonadec", "octadec", "heptadec", "hexadec", "pentadec", "tetradec", "tridec",
         "dodec", "undec", "dec", "non", "oct", "hept", "hex", "pent", "but", "prop", "eth", "meth"]
def chain(s):
    c = re.sub(r"\d", "", compact(s))
    for h in HAL + ["di"]:
        c = c.replace(h, "")
    for ch in CHAIN:           # 긴 것부터 → 가장 긴 주사슬 이름
        if ch in c:
            return "icos" if ch == "eicos" else ch
    return ""

SUF = [("oicacid", "oic acid"), ("diol", "diol"), ("ol", "ol"), ("one", "one"), ("al", "al"),
       ("yne", "yne"), ("ene", "ene"), ("ane", "ane")]
def suffix(s):
    c = re.sub(r"\d", "", compact(s))
    for k, v in SUF:
        if c.endswith(k):
            return v
    return "?"

def score():
    import jiwer
    from py2opsin import py2opsin
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    def can(s):
        m = Chem.MolFromSmiles(s) if s else None
        return Chem.MolToSmiles(m) if m else None

    rs = rows()
    hyp = {r["audio_id"]: r["asr_output"] for r in csv.DictReader(open(RAW, encoding="utf-8-sig"))}
    hyps = [clean(hyp.get(r["audio_id"], "")) for r in rs]
    smi = py2opsin([h if h else "x" for h in hyps])

    out = []
    for r, h, s in zip(rs, hyps, smi):
        ref = r["reference_text"]
        a, b = can(s), can(r["canonical_smiles"])
        e = {
            "audio_id": r["audio_id"], "class": r["class"], "reference_text": ref,
            "asr_output": hyp.get(r["audio_id"], ""),
            "exact": int(h == ref.lower()),
            "compact": int(compact(h) == compact(ref)),
            "cer": round(jiwer.cer(compact(ref), compact(h) or "-"), 4),
            "opsin_parse": int(a is not None),
            "struct_match": int(a is not None and a == b),
            "err_locant": int(locants(h) != locants(ref)),
            "err_halogen": int(halogens(h) != halogens(ref)),
            "err_chain": int(chain(h) != chain(ref)),
            "err_suffix": int(suffix(h) != suffix(ref)),
            "asr_smiles": s or "",
        }
        out.append(e)

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    n = len(out)
    pct = lambda k, xs=out: 100 * sum(x[k] for x in xs) / max(len(xs), 1)
    print(f"\n===== 전체 {n}개 =====")
    print(f"Exact match (표기까지 동일)   : {pct('exact'):5.1f}%")
    print(f"Compact match (표기 차이 무시): {pct('compact'):5.1f}%")
    print(f"평균 CER (compact 기준)       : {100*sum(x['cer'] for x in out)/n:5.2f}%")
    print(f"OPSIN 해석 가능               : {pct('opsin_parse'):5.1f}%")
    print(f"구조 일치 (struct_match)      : {pct('struct_match'):5.1f}%   ← ASR 그대로 썼을 때 올바른 분자가 나오는 비율")
    print("\n--- 오류 유형 (전체 대비 %) ---")
    for k, name in [("err_locant", "위치번호"), ("err_halogen", "할로젠"), ("err_chain", "주사슬 길이"), ("err_suffix", "접미사")]:
        print(f"{name:8s}: {pct(k):5.1f}%")
    print("\n--- 클래스별 구조 일치 / compact 일치 ---")
    for c in sorted({x["class"] for x in out}, key=lambda c: -sum(x["class"] == c for x in out)):
        xs = [x for x in out if x["class"] == c]
        print(f"{c:13s} n={len(xs):4d}  struct {pct('struct_match', xs):5.1f}%  compact {pct('compact', xs):5.1f}%")
    print("\n--- 구조가 틀린 예시 20개 ---")
    for x in [x for x in out if not x["struct_match"]][:20]:
        print(f"{x['reference_text']:32s} → {x['asr_output']}")
    print(f"\n저장: {OUT}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("gen", "all"): asyncio.run(_gen())
    if cmd in ("asr", "all"): asr()
    if cmd in ("score", "all"): score()
