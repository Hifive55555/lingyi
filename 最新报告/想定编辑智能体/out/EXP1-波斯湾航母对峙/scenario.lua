-- ============================================================
-- 想定：波斯湾航母对峙
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:58:22
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-波斯湾航母对峙.scen
-- 规模：单元 6 型 / 11 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='波斯湾航母对峙', DURATION=10800, COMPLEXITY=2, DIFFICULTY=2, SEED=58906, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuazouaWr+a5vuiIquavjeWvueWzmTwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5rOi5pav5rm+6Iiq5q+N5a+55bOZPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgMTAg5pyIIDEg5pelIDE4IOaXtu+8jOazouaWr+a5vuOAgue6ouaWuSAxIOS4quiIquavjeaJk+WHu+e+pO+8jDEg6ImY6L695a6B6Iiw44CBMiDoiZggMDUyROOAgTEg6ImYIDA5MyDmvZzoiYc8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuS7juilv+WMlyAxMDAg5rW36YeM6L+b5YWl77yb6JOd5pa5IDEg6ImY5bC857Gz5YW557qn44CBMiDoiZjkvK/lhYvnuqfku47kuJzljZcgMTIwIOa1t+mHjOi/m+WFpe+8jDQg5p62IEYvQS0xOEUg5omn6KGM5Y+N6Iiw5omT5Ye744CCPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7nuqLmlrnmiafooYzlj43oiLDlt6HpgLvvvIzljYrlvoQgNDAg5rW36YeM44CC5rW35Ya1IDYg57qn77yM5LqR6YePIDAuOe+8jOmZjembqCAzMOOAguaMgee7rSAzIOWwj+aXtuOAguiwqOaFjuW8gOeBq+OAgjwvU1BBTj48L1A+PC9CT0RZPg=='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=52.1289, CAMERALAT=26.3821, CAMERAALT=939329.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=52.1289, CAMERALAT=26.3821, CAMERAALT=939329.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 30, 0.9, 6)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 辽宁舰 #1', dbid=2007.0, latitude='27.678511', longitude='50.683131', heading=45})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #2', dbid=2296.0, latitude='27.666890', longitude='50.533141', heading=45, count=2.0})
U_3 = AddUnit({side=%{S:红方}, type='Submarine', DATASOURCE=0.0, name='红方 093 #3', dbid=164.0, latitude='27.831465', longitude='50.436464', heading=45})
U_4 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 尼米兹 #1', dbid=341.0, latitude='25.085786', longitude='53.580243', heading=225})
U_5 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #2', dbid=112.0, latitude='25.097407', longitude='53.726903', heading=225, count=2.0})
U_6 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F/A-18E #3', dbid=753.0, latitude='24.932832', longitude='53.821434', alt=8000.0, heading=225, loadoutid=4617.0, count=4.0})

-- [6] 创建任务
-- 蓝方-反舰打击（Patrol/NAVAL=反舰）
M_1 = AddMission(%{S:蓝方}, '蓝方-反舰打击', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 蓝方-反舰打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='91c5d0c0-8873-5ed9-9196-f1aa082cfa8b', name='蓝方-反舰打击-WP1', lat=25.451154, lon=54.16479, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='75651a68-c790-591c-8344-ec1527c2e27b', name='蓝方-反舰打击-WP2', lat=24.626196, lon=54.16479, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='bed7a31b-844b-5d04-9204-cba68c6799a6', name='蓝方-反舰打击-WP3', lat=24.626196, lon=53.254263, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='b7a34de7-fdf5-56a0-8e41-9916d8309c01', name='蓝方-反舰打击-WP4', lat=25.451154, lon=53.254263, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰打击}, {patrolZone={'91c5d0c0-8873-5ed9-9196-f1aa082cfa8b', '75651a68-c790-591c-8344-ec1527c2e27b', 'bed7a31b-844b-5d04-9204-cba68c6799a6', 'b7a34de7-fdf5-56a0-8e41-9916d8309c01'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='489f2ef9-077a-5fab-b294-491a259902b9', name='红方-反舰巡逻-WP1', lat=28.144105, lon=51.140427, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='390abab1-7045-50af-83fa-7942339250a7', name='红方-反舰巡逻-WP2', lat=27.201296, lon=51.140427, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='ba0da060-47b8-561f-81db-3ee29cf05c4d', name='红方-反舰巡逻-WP3', lat=27.201296, lon=50.075845, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='e0f92bdd-b677-5e48-80a5-3cb6030e2ae7', name='红方-反舰巡逻-WP4', lat=28.144105, lon=50.075845, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'489f2ef9-077a-5fab-b294-491a259902b9', '390abab1-7045-50af-83fa-7942339250a7', 'ba0da060-47b8-561f-81db-3ee29cf05c4d', 'e0f92bdd-b677-5e48-80a5-3cb6030e2ae7'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:蓝方 尼米兹 #1},%{U:蓝方 伯克级 #2},%{U:蓝方 F/A-18E #3}', %{M:蓝方-反舰打击}, false)
AssignUnitListToMission('%{U:红方 辽宁舰 #1},%{U:红方 052D #2},%{U:红方 093 #3}', %{M:红方-反舰巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-波斯湾航母对峙.scen')
