# 讓 AI Agents 團隊幫您自動訓練電腦視覺模型 - 以 YOLO 模型在 Wafer dataset 圖像為例

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/kevin801221/auto-cv-train-inference-optimization/actions/workflows/ci.yml/badge.svg)](https://github.com/kevin801221/auto-cv-train-inference-optimization/actions)

> **EN** — Change one YAML, run one command: auto-pipeline any Roboflow dataset through **download → validate/split → train → hyperparameter-optimize → inference visualization**. Or just talk to Claude Code — 5 specialist agents run the whole pipeline for you.
>
> **中** — 改一個 YAML，一行指令把任何 Roboflow 資料集自動跑完「下載 → 驗證切分 → 訓練 → 超參優化 → 推論視覺化」；或者直接跟 Claude Code 對話，5 個專家 agent 自動接力做完。

半導體晶圓瑕疵偵測（WM-811K）內建 showcase：**mAP@0.5 = 0.9913**。

---

## 30-second quickstart / 30 秒上手

```bash
git clone git@github.com:kevin801221/auto-cv-train-inference-optimization.git
cd auto-cv-train-inference-optimization
uv venv --python 3.11 && uv pip install -e .
cp .env.example .env          # fill in ROBOFLOW_API_KEY / 填入 Roboflow API key
uv run autocv all -c configs/wafer.yaml --yes
```

## Two interfaces / 兩種介面

**1. CLI**

| Command | Does |
|---|---|
| `autocv data -c configs/wafer.yaml` | download from Roboflow / 下載 |
| `autocv split -c ...` | validate labels + split 70/20/10 / 驗證切分 |
| `autocv train -c ...` | train YOLOv8 (asks before burning GPU) / 訓練（先問再燒卡） |
| `autocv optimize -c ...` | hyperparameter search / 超參搜尋 |
| `autocv infer -c ...` | inference + bbox PNGs + summary / 推論視覺化 |
| `autocv all -c ... [--optimize]` | full pipeline / 一條龍 |

**2. Claude Code agents** — open this repo in Claude Code and say *"download and train this dataset"*. Five agents (data-hunter → bbox-labeler → training-runner → hp-optimizer → inference-runner) hand off automatically. 用 Claude Code 打開本 repo，說「下載並訓練」，5 個 agent 自動接力。

## Bring your own dataset / 換你自己的資料集

Copy `configs/template.yaml`, change `roboflow.workspace/project/version`. No code change. 複製 `configs/template.yaml` 改 workspace/project/version 即可，不用改任何程式碼。

## Showcase results / 成果展示

| Metric | Value |
|---|---|
| mAP@0.5 | 0.9913 |
| mAP@0.5:0.95 | 0.7633 |
| Precision | 0.9331 |
| Recall | 0.9968 |

See [`docs/results/summary.md`](docs/results/summary.md) for 10 bbox visualizations. 10 張帶 bbox 視覺化見該檔。

## Responsible training / 負責任訓練

`train` and `optimize` print a time estimate and **wait for your confirmation** before consuming GPU/electricity. Agents are forbidden from using `--yes`. 訓練/優化前一定先報預估時間並等你確認，agent 不准跳過。

## Architecture / 架構

See [`docs/architecture.md`](docs/architecture.md).

## License

MIT
