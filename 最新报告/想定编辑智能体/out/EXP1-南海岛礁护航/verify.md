# 想定验收报告：南海岛礁护航

**结论：PASS**（通过 18/18 项）

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 文件已落盘且非空 | PASS | 48450 字节 |
| 2 | 引擎可回读（GetScenarioContent） | PASS | 回读 253421 字节 |
| 3 | 标题一致 | PASS | spec='南海岛礁护航' engine='南海岛礁护航' |
| 4 | 推演时长一致 | PASS | spec=14400s engine=14400s |
| 5 | 推演方集合一致 | PASS | spec=['红方', '蓝方'] engine=['红方', '蓝方'] |
| 6 | 两两对抗关系正确 | PASS | 全部一致（H=3 U=2 F=1 N=0） |
| 7 | 兵力数量分布一致 | PASS | 红方 Aircraft:4, Ship:4, Submarine:0, Facility:0, Satellite:0；蓝方 Aircraft:2, Ship:3, Submarine:0, Facility:0, Satellite:0 |
| 8 | 单元齐全（按 推演方+名称） | PASS | 7 型单元全部在册 |
| 9 | 单元 DBID 正确 | PASS | 全部一致 |
| 10 | 单元初始坐标正确（±0.002°） | PASS | 全部一致 |
| 11 | 任务齐全（推演方+名称） | PASS | 3 个任务全部在册 |
| 12 | 任务类型/子类型正确 | PASS | 全部一致 |
| 13 | 巡逻区顶点数正确（Patrol） | PASS | 全部一致 |
| 14 | 单元-任务分配数正确 | PASS | 全部一致 |
| 15 | 没有多余任务 | PASS | OK |
| 16 | 条令关键字段一致 | PASS | 全部一致 |
| 17 | 气象一致 | PASS | spec={'temp': 20, 'rainfall': 0, 'cloud': 0.7, 'seastate': 5} engine={'temp': 20, 'rainfall': 0, 'cloud': 0.7, 'seastate': 5} |
| 18 | 词表提示 | PASS | 提示：单元 蓝方 伯克级 #1 的别名 '伯克级' 与引擎类名 '“阿利伯克”级导弹驱逐舰' 不完全一致 |
