# 先读 AGENTS.md

本仓库的所有硬约束（绝对路径规则、目录/打包/部署三处同改、编码 BOM、无 venv、
小窗必须自带 WebView2、安装包低权限…）和**改完必跑的验证命令**都写在
[`AGENTS.md`](AGENTS.md)，它是唯一权威。

补充两点：

- 改战法（`Mission_all_*.py` 的任务/坐标/BOL）→ 先看 `AGENTS.md` §3，
  跑 `智能体代码/tools/check_table*.py`，必须输出 `结论: 全部一致`
- 改任何文件前跑一次 `./verify.sh` 拿到基线，改完再跑，两次都绿才提交
