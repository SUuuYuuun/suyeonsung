# Suyeon Sung | 성수연

**Materials Science & Engineering · Undergraduate Researcher**

[GitHub ↗](https://github.com/SUuuYuuun)

---

## About Me

- **Soongsil University** — 신소재공학과
- **FNML Lab · Undergraduate Researcher** — 숭실대학교 신소재공학과 학부연구생, 신근영 교수 연구실 (2026-2 ~)
  - Track: **B — Doped Graphene (N/P-doped Graphene)**
  - Topic: 질소/인 도핑 그래핀 기반 박막 전자파(EMI) 차폐 필름 연구 — GO 환원·도핑 공정 확립, XPS·Raman 특성 분석, 도핑 함량별 차폐 성능 평가
- **Seoul National University · Undergraduate Research Intern** — 서울대학교 학부생 연구인턴, 김남준 교수 연구실 (2026-2 ~)
  - Track: **AI with NVIDIA: Multimodal & Efficient Computing**
  - Topic: 화학명 음성인식(ASR) 오류를 화학 검증 기반 Agentic LLM으로 보정해 분자구조를 복원하는 연구

소재의 구조와 물성을 이해하고, **데이터 기반으로 분석하고 검증하는** 공학도를 목표로 공부하고 있습니다.

---

## Awards

| Competition | Award |
| --- | --- |
| 제2회 AI·SW 창작 콘텐츠 공모전 (산문 부문) — 「보안문자를 입력하세요」 | **우수상** |
| 제16회 숭실 캡스톤 디자인 경진대회 | **장려상** |
| 제3회 숭실 재학생 학습법 경진대회 — AX (Ai eXperience) 인터랙티브 콘텐츠 공모전 | **장려상** |

---

## Projects

### Speech-to-Molecule: 화학명 ASR 오류 보정 연구 *(진행 중)*
`서울대학교 학부생 연구인턴` 팀 연구 · 김남준 교수 연구실 · 2026-2 ~

> 음성으로 말한 IUPAC 화학명이 ASR에서 깨지는 문제를 분석하고, LLM으로 올바른 화학명을 복원해 분자구조(SMILES)까지 재구성

```
IUPAC Name → Spoken Text → TTS → ASR (Whisper large-v3) → LLM 오류 보정 → OPSIN / RDKit 검증 → SMILES · 분자구조
```

- **Motivation** — 일반 ASR은 화학 전문용어에서 오류가 잦고, `2-methyl → 3-methyl`처럼 한 글자만 틀려도 다른 분자가 됨. 정확한 이름을 구조로 바꾸는 도구(OPSIN)는 강하지만 오류가 섞인 이름에는 취약 → 그 사이를 LLM으로 메우는 것이 목표
- **Scope** — 영어 · IUPAC 이름 기준, 범용 LLM(GPT · Gemini · Claude)으로 오류 보정을 먼저 시험한 뒤 개선 방향 결정
- **My Role — 화학명 TTS 음성 데이터셋 구축**
  - IUPAC 화학명 5,000개 중 1차 실험용 1,000개(pilot set)를 TTS 음성으로 변환
  - 숫자·기호 오독을 막기 위한 발음용 텍스트 변환 규칙 적용 (예: `3,5-difluoroundecane` → `3 5 difluoroundecane`)
  - edge-tts (en-US-AriaNeural) → mp3 + 16 kHz mono WAV, 파일별 정답 화학명을 담은 manifest로 ASR 오류율 측정 준비
- **Next** — Whisper large-v3로 ASR 오류율·오류 유형(위치번호 · 할로젠 · 접미사) 분석 → LLM 보정 전·후 비교
- **Keywords** — ASR · TTS · LLM · Agentic AI · IUPAC Nomenclature · SMILES · OPSIN · RDKit

### FD-SOI MOSFET 부분 박막 BOX 구조 TCAD 분석
`반도체집적공정` 과목 팀 프로젝트 · 2026 · 5인 팀

> 부분 박막 BOX 구조를 이용한 FD-SOI MOSFET의 Back-Bias Coupling 향상 및 Substrate Isolation Trade-off 분석

- **Tool** — Synopsys Sentaurus TCAD (SProcess · SDevice · SVisual)
- **Goal** — FD-SOI NMOS에서 BOX 두께에 따른 back-bias coupling(γ<sub>back</sub>)과 substrate isolation의 trade-off를 정량 분석하고, 채널 직하만 BOX를 얇게 만든 **부분 박막 BOX(locally-thinned BOX)** 구조 제안
- **Results**
  - 균일 BOX 10–40 nm sweep → γ<sub>back</sub> ∝ 1/t<sub>BOX</sub> 선형 관계 확인 (R² = 0.981), capacitive divider 모델 검증
  - 제안 구조(채널 직하 BOX 20 nm) → thick BOX 대비 coupling **+39.6%**, thin BOX 대비 off-leakage **약 64배 감소**
  - 기판 전위·BOX 전계 분포 분석으로 균일 BOX로는 불가능한 coupling–isolation 동시 확보 동작점 확인
- **Keywords** — FD-SOI · Back-Bias · BOX Scaling · Device Simulation · TCAD

### MIS / MIM 커패시터 제작 및 전기적 특성 평가
`신소재공학실험2` 반도체 실습 · 2026-2

> 웨이퍼 절단부터 유전막 증착, 전극 패터닝, C-V 측정까지 — 커패시터 소자 하나를 처음부터 끝까지 직접 만들고 평가

```
Dicing → ALD (TiO₂) → 두께 평가 → Evaporator (Al 전극) → 전극막 평가 → C-V 측정
```

| 단계 | 내용 | 장비 |
| --- | --- | --- |
| **① 유전막 증착** | p-Si / p⁺⁺-Si 기판에 TiO₂ ALD 증착 (Ti(Me₅Cp)(OMe)₃ / O₃, 500·680·862 cycle → 약 15–25 nm) | Diamond pen, ALD |
| **② 유전막 두께 평가** | Cycle 수에 따른 증착 두께·선형성 평가, 광학 두께 vs 면밀도 환산 두께 비교·고찰 | Ellipsometry, XRF |
| **③ 상부 전극 형성** | Shadow mask를 이용한 Al 상부 전극 열증착 및 패터닝 → MIS(Al/TiO₂/p-Si), MIM(Al/TiO₂/p⁺⁺-Si) 구조 제작 | Thermal Evaporator |
| **④ 전극막 평가** | Al 두께별 면저항 측정 → 비저항 산출 및 두께 의존성 분석, SEM 표면 morphology·grain size 분석 | Stylus Profiler, 4-point probe, SEM |
| **⑤ 전기적 특성 평가** | 전극 면적 측정, TiO₂ 두께·기판 종류에 따른 C-V 특성 측정 (accumulation–depletion–inversion) | Optical Microscope, Probe station |

- **Keywords** — 반도체 공정 · 박막 증착 · ALD · PVD · 박막 계측 · MOS Capacitor · C-V

---

## Certifications

| Certification | Grade |
| --- | --- |
| ADsP (데이터분석 준전문가) | **취득** |
| TOEIC Speaking | **IH** |

---

## Activities

- **숭실대학교 중앙 스트릿댄스 동아리 플레이버(Flavor)** — 학교 축제 공연, 정기공연 등 참여
