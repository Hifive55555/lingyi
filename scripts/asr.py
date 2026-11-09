#!/usr/bin/env python
"""
视频音轨 → 带时间码转写
=======================
PyAV 抽 16k 单声道 → faster-whisper (VAD 开) → srt + jsonl(逐段) + txt

为什么用 VAD：讲解视频中间常有静默/翻页声，不开 VAD 的 whisper
会在无语音段编造字幕。

用法：
  python scripts/asr.py --video 讲解/智能体讲解.mp4 --out work/jj/audio --model large-v3
"""
import argparse
import json
import os
import sys
import time

import av
import numpy as np


def extract_audio(video, wav_path, sr=16000):
    """顺序解码音轨 → 16k 单声道 → 写 raw f32（避免依赖 soundfile）"""
    c = av.open(video)
    st = next(s for s in c.streams if s.type == "audio")
    try:
        st.thread_type = "AUTO"
    except Exception:
        pass
    res = av.AudioResampler(format="flt", layout="mono", rate=sr)
    chunks = []
    for frame in c.decode(st):
        for f in res.resample(frame):
            chunks.append(f.to_ndarray().reshape(-1))
    for f in res.resample(None):
        chunks.append(f.to_ndarray().reshape(-1))
    c.close()
    audio = np.concatenate(chunks).astype(np.float32)
    np.save(wav_path, audio)
    return audio, sr


def fmt(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--lang", default="zh")
    ap.add_argument("--download-root",
                    default=os.path.expanduser("~/.cache/huggingface/whisper"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    wav = os.path.join(args.out, "audio.npy")
    if os.path.exists(wav):
        audio = np.load(wav)
        print(f"复用已抽音轨 {wav}  {len(audio)/16000/60:.1f} min")
    else:
        t0 = time.time()
        audio, sr = extract_audio(args.video, wav)
        print(f"抽音轨 {len(audio)/sr/60:.1f} min，耗时 {time.time()-t0:.0f}s")

    # 音量包络：判断是否真有语音
    win = 16000
    env = np.array([np.sqrt((audio[i:i + win] ** 2).mean())
                    for i in range(0, len(audio) - win, win)])
    db = 20 * np.log10(env + 1e-9)
    print(f"音量包络 dB: p10={np.percentile(db,10):.1f} "
          f"p50={np.percentile(db,50):.1f} p90={np.percentile(db,90):.1f}")

    from faster_whisper import WhisperModel
    t0 = time.time()
    model = WhisperModel(args.model, device="cpu", compute_type="int8",
                         download_root=args.download_root)
    print(f"模型就绪 {time.time()-t0:.0f}s")

    segments, info = model.transcribe(
        audio, language=args.lang, vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        beam_size=5, condition_on_previous_text=False,
        initial_prompt="以下是一段关于兵棋推演智能体设计的讲解，涉及空战、舰船自卫、地空导弹、"
                       "灵弈智能推演平台、条令、挂载、导弹型号等术语。",
    )
    print(f"检测语言 {info.language} p={info.language_probability:.2f} "
          f"时长 {info.duration:.0f}s")

    rows, srt = [], []
    for i, s in enumerate(segments, 1):
        row = {"i": i, "start": round(s.start, 2), "end": round(s.end, 2),
               "text": s.text.strip()}
        rows.append(row)
        srt.append(f"{i}\n{fmt(s.start)} --> {fmt(s.end)}\n{s.text.strip()}\n")
        print(f"[{fmt(s.start)}] {s.text.strip()}", flush=True)
        # 增量落盘，防止长任务中断丢结果
        if i % 20 == 0:
            json.dump(rows, open(os.path.join(args.out, "segments.json"),
                                 "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)

    json.dump({"video": args.video, "model": args.model, "lang": info.language,
               "duration": info.duration, "segments": rows},
              open(os.path.join(args.out, "segments.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(args.out, "transcript.srt"), "w",
         encoding="utf-8").write("\n".join(srt))
    open(os.path.join(args.out, "transcript.txt"), "w", encoding="utf-8").write(
        "\n".join(f"[{fmt(r['start'])}] {r['text']}" for r in rows))
    print(f"\n完成 {len(rows)} 段 → {args.out}/")


if __name__ == "__main__":
    main()
