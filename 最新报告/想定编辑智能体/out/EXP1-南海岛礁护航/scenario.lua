-- ============================================================
-- 想定：南海岛礁护航
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:55:49
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-南海岛礁护航.scen
-- 规模：单元 7 型 / 13 个；任务 3 个；参考点 12 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='南海岛礁护航', DURATION=14400, COMPLEXITY=2, DIFFICULTY=2, SEED=73793, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuWNl+a1t+Wym+ekgeaKpOiIqjwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5Y2X5rW35bKb56SB5oqk6IiqPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgOCDmnIggMTUg5pelIDA3IOaXtu+8jOWNl+a1t+S4remDqOOAgue6ouaWuSAxIOiJmOWxseS4nOiIsOOAgTIg6ImYIDA1MkTjgIExIOiJmCAwNTRBIOS7juWMl+S+pyAxMjAg5rW36YeM5Y2X5LiL77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7miafooYzliLbmtbflt6HpgLvvvIzlt6HpgLvljYrlvoQgNTAg5rW36YeM77ybNCDmnrbmrbwtMTUg5omn6KGM6Ziy56m65beh6YC777yb6JOd5pa5IDIg6ImY5Lyv5YWL57qn44CBMSDoiZjmj5DlurflvrfnvZfliqA8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuS7juS4nOWNlyAxNTAg5rW36YeM5o6l6L+R77yMMiDmnrYgRi9BLTE4RSDmiafooYzlj43oiLDmiZPlh7vjgILmtbflhrUgNSDnuqfvvIzkupHph48gMC4344CC5oyB57utIDQg5bCP5pe244CC6Ieq55Sx5byA54Gr44CCPC9TUEFOPjwvUD48L0JPRFk+'})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=115.4173, CAMERALAT=16.2328, CAMERAALT=1195218.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=115.4173, CAMERALAT=16.2328, CAMERAALT=1195218.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.7, 5)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 山东舰 #1', dbid=3187.0, latitude='18.000000', longitude='114.500000', heading=45})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #2', dbid=2296.0, latitude='17.988379', longitude='114.360339', heading=45, count=2.0})
U_3 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #3', dbid=1965.0, latitude='18.152954', longitude='114.270318', heading=45})
U_4 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='红方 歼-15 #4', dbid=2496.0, latitude='18.386370', longitude='114.391145', alt=8000.0, heading=45, loadoutid=3.0, count=4.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #1', dbid=112.0, latitude='14.232233', longitude='116.339007', heading=225, count=2.0})
U_6 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 提康德罗加 #2', dbid=110.0, latitude='14.243854', longitude='116.476039', heading=225})
U_7 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F/A-18E #3', dbid=753.0, latitude='14.079279', longitude='116.564364', alt=8000.0, heading=225, loadoutid=4617.0, count=2.0})

-- [6] 创建任务
-- 红方-制海巡逻（Patrol/SEACONTROL=制海）
M_1 = AddMission(%{S:红方}, '红方-制海巡逻', 'Patrol', {isactive=true, type='SEACONTROL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-防空巡逻（Patrol/AAW=防空）
M_2 = AddMission(%{S:红方}, '红方-防空巡逻', 'Patrol', {isactive=true, type='AAW', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击（Patrol/NAVAL=反舰）
M_3 = AddMission(%{S:蓝方}, '蓝方-反舰打击', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-制海巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='6d0073f7-bae2-56ab-b333-f5c48f209403', name='红方-制海巡逻-WP1', lat=18.636367, lon=114.996632, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='432d81fb-e3bc-5836-a92e-f0ef87b9ed51', name='红方-制海巡逻-WP2', lat=17.457855, lon=114.996632, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='eacbf3ba-22d9-5032-b998-2dfb4dc9f185', name='红方-制海巡逻-WP3', lat=17.457855, lon=113.75714, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='48804ff8-b739-512b-ac9c-70b4e30e7e50', name='红方-制海巡逻-WP4', lat=18.636367, lon=113.75714, highlighted=true})
SetMission(%{S:红方}, %{M:红方-制海巡逻}, {patrolZone={'6d0073f7-bae2-56ab-b333-f5c48f209403', '432d81fb-e3bc-5836-a92e-f0ef87b9ed51', 'eacbf3ba-22d9-5032-b998-2dfb4dc9f185', '48804ff8-b739-512b-ac9c-70b4e30e7e50'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-防空巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='59b6e6e4-7341-52be-9ce4-3fd8bfd601fd', name='红方-防空巡逻-WP1', lat=18.798849, lon=114.825813, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='eeb10897-f359-52a3-bf65-a1a02bbbd5e4', name='红方-防空巡逻-WP2', lat=17.973891, lon=114.825813, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='e2cf75d5-e525-5bec-b6eb-ad42b8275be7', name='红方-防空巡逻-WP3', lat=17.973891, lon=113.956477, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='920c455b-3e0d-5f34-9ca0-2ccc56cc3dd2', name='红方-防空巡逻-WP4', lat=18.798849, lon=113.956477, highlighted=true})
SetMission(%{S:红方}, %{M:红方-防空巡逻}, {patrolZone={'59b6e6e4-7341-52be-9ce4-3fd8bfd601fd', 'eeb10897-f359-52a3-bf65-a1a02bbbd5e4', 'e2cf75d5-e525-5bec-b6eb-ad42b8275be7', '920c455b-3e0d-5f34-9ca0-2ccc56cc3dd2'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='aaff3df9-cb67-5be0-8c7f-e3fe540f1561', name='蓝方-反舰打击-WP1', lat=14.597601, lon=116.885255, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='bea0b10a-8829-596d-a491-dd78c7bcca2b', name='蓝方-反舰打击-WP2', lat=13.772643, lon=116.885255, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='3cb06baf-727b-52f4-a883-27ad463412a7', name='蓝方-反舰打击-WP3', lat=13.772643, lon=116.034352, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='319c256f-0b0d-50d4-a5bd-15c6fba9547f', name='蓝方-反舰打击-WP4', lat=14.597601, lon=116.034352, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰打击}, {patrolZone={'aaff3df9-cb67-5be0-8c7f-e3fe540f1561', 'bea0b10a-8829-596d-a491-dd78c7bcca2b', '3cb06baf-727b-52f4-a883-27ad463412a7', '319c256f-0b0d-50d4-a5bd-15c6fba9547f'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 山东舰 #1},%{U:红方 052D #2},%{U:红方 054A #3}', %{M:红方-制海巡逻}, false)
AssignUnitListToMission('%{U:红方 歼-15 #4}', %{M:红方-防空巡逻}, false)
AssignUnitListToMission('%{U:蓝方 伯克级 #1},%{U:蓝方 提康德罗加 #2},%{U:蓝方 F/A-18E #3}', %{M:蓝方-反舰打击}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-南海岛礁护航.scen')
