# data/：平台在环实验的派生数据（生成物）

> **生成时间**：2026-11-18 00:10 (+08:00)
> **生成命令**：`~/.venvs/ai-dev/bin/python analysis/metrics.py`（`--runs raw/runs.jsonl --tap raw/tap --out data`，bootstrap `n_boot=1000`，种子 `20261118`）
> **同批生成的图**：`fig/fig_*.png|svg`（`analysis/figs.py`，300 dpi）
> **口径与证据链**：见 `analysis/README.md`

## 输入清单（远端只读快照）

远端来源：靶机 `Hifive@10.42.97.205`，目录 `D:/LingYi/exp/v2`。批量实验**仍在运行**，本目录是时刻快照，不是最终结果。

| 本地文件 | 远端路径 | 字节 | sha256 |
| --- | --- | --- | --- |
| `raw/runs.jsonl` | `D:/LingYi/exp/v2/runs.jsonl` | 1526 | `465631f13fd18c7cf7bdf9e2bc942ba767679f8c9c84dd765cf8dd84fbc90886` |
| `raw/tap/A0_new__1794930962__红方.jsonl` | `D:/LingYi/exp/v2/tap/` 同名 | 3511636 | `42ef0eb994c81fef960487c1d906cee837545de7ec8cc3cf1f393269a25dc0c3` |
| `raw/tap/A0_new__1794930962__蓝方.jsonl` | 同上 | 3608517 | `c5e8aa5c5e2448d71e677ef9c9d4e5f038509a183b0b77c3641bbdb77f9b52aa` |
| `raw/tap/A0_new__1794931152__红方.jsonl` | 同上 | 1213299 | `66c33734fc393deaca9e17f00d58c02d9a966ddc2ac27d13376b771eb4c628ae` |
| `raw/tap/A0_new__1794931152__蓝方.jsonl` | 同上 | 1148351 | `57a9386d716c2b8a6f2db0bfa64ba8f3b38b6476d7c853f4ceb843a3220a6888` |
| `raw/tap/A0_new__1794931292__红方.jsonl` | 同上 | 1608546 | `55d036efeadbb856ee8dd530d307a58f7846975bcb765df1eda5b42539b85cf6` |
| `raw/tap/A0_new__1794931292__蓝方.jsonl` | 同上 | 1549189 | `f93ee5b519e3ce0ca415b5b23c18ba6ac621796568441a17914f65940d4c6e67` |
| `raw/tap/A0_new__1794931446__红方.jsonl` | 同上 | 3574291 | `ad12389ae2de6ca36f1ae365d5f36f18fbb1d67410814ad112611a5c967f4ea9` |
| `raw/tap/A0_new__1794931446__蓝方.jsonl` | 同上 | 3587532 | `b5f475f05d1d727951612a4a456e7d1c0631a3f7ae8dceab5d49c3fe60032ad3` |

`sha256sum` 在 `raw/` 目录下复核：`sha256sum runs.jsonl tap/*.jsonl`。

`tap_sample/`（`runs_sample.jsonl` + `T1__红方.jsonl`）是开发自测用本地样本，**不参与**本目录生成。

## 输出清单

| 文件 | 行数 | 内容 |
| --- | --- | --- |
| `runs.csv` | 4 局 | 已对齐 tap 的对局结果（字段取自 `runs.jsonl`，附 `tap_file_red/blue`、`tap_steps`） |
| `episode_metrics.csv` | 4 局 | 每局派生指标 35 列（含 `tap/arm/episode` 标识列）：损失、得分、交战强度、耗时、满时长等 |
| `arm_summary.csv` | 28 行 = 1 arm × 28 metric | 按 arm 聚合：`n/mean/std` + bootstrap 95% CI（`ci_low/ci_high/n_boot`） |

覆盖范围：**arm = `A0_new`，n = 4**（`steps` 361 / 107 / 146 / 361，`sim_end` 10800.3 / 3164.3 / 4339.3 / 10800.3）。
2/4 局满时长（`full_length=1`），另 2 局平台在胜负已定时提前结束（`ok=true`、`winner=1`），非数据缺失。
一致性自检：4/4 局的 tap 派生得分/步数与 `runs.jsonl` 登记值相等（`metrics.py` stdout 输出）。

## 重跑

```bash
cd 最新报告/实验v2
# 1) 重拉远端最新快照（只读，不影响正在跑的批量实验），步骤见 analysis/README.md §4
# 2) 重算
~/.venvs/ai-dev/bin/python analysis/metrics.py
~/.venvs/ai-dev/bin/python analysis/figs.py
```

重跑会覆盖本目录三个 CSV 与 `fig/` 四张图；`raw/` 只由拉取步骤更新。
若远端实验仍在进行，重跑后请同步更新本文件顶部的「生成时间」与上方输入清单。
