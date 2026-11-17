-- ============================================================
-- 想定：东海反舰遭遇战-V12
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 21:03:21
-- 保存路径：D:/LingYi/Data/Scenarios/东海反舰遭遇战-V12.scen
-- 规模：单元 5 型 / 20 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='东海反舰遭遇战-V12', DURATION=10800, COMPLEXITY=2, DIFFICULTY=2, SEED=98863, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuS4nOa1t+WPjeiIsOmBremBh+aImC1WMTI8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuagh+mimO+8muS4nOa1t+WPjeiIsOmBremBh+aImDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+6K6+5a6aIDIwMjYg5bm0IDMg5pyIIDEg5pel5LiK5Y2IIDgg5pe277yM5Lic5rW35Lit6YOo44CC57qi5pa5IDIg6ImYIDA1MkTjgIExIOiJmCAwNTRBIOS7juilv+S+pyAxMTAg5rW36YeM6L+b5YWl77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7miafooYzlj43oiLDlt6HpgLvvvIzlt6HpgLvljYrlvoQgNDAg5rW36YeM77yb6JOd5pa5IDEg5Liq6Iiq5q+N5omT5Ye7576k77yMMSDoiZjnpo/nibnnuqfjgIEyIOiJmOS8r+WFi+e6p+WcqOS4nOS+pyAxMzAg5rW36YeM77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj40IOaetiBGLTM1QyDmiafooYzlj43oiLDmiZPlh7vjgILmtbflhrUgNCDnuqfvvIzkupHph48gMC4244CC5oyB57utIDMg5bCP5pe244CC5Y+M5pa56Ieq55Sx5byA54Gr44CCPC9TUEFOPjwvUD48L0JPRFk+'})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=123.7652, CAMERALAT=28.6179, CAMERAALT=1003107.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=123.7652, CAMERALAT=28.6179, CAMERAALT=1003107.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.6, 5)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #1', dbid=2296.0, latitude='27.203638', longitude='125.475122', heading=90.0, count=4.0})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #2', dbid=1965.0, latitude='27.101498', longitude='125.572645', heading=90.0, count=2.0})
U_3 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 福特级 #1', dbid=506.0, latitude='30.082065', longitude='122.256674', heading=270.0, count=2.0})
U_4 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #2', dbid=112.0, latitude='30.134204', longitude='122.159151', heading=270.0, count=4.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F-35C #3', dbid=824.0, latitude='30.078371', longitude='121.957846', alt=8000.0, heading=270.0, loadoutid=3004.0, count=8.0})

-- [6] 创建任务
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_1 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:蓝方}, '蓝方-反舰打击', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='33d4a119-9e75-5551-a756-ba45928810b7', name='红方-反舰巡逻-WP1', lat=27.819216, lon=125.523904, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='a19332b1-a2f2-5d58-98b5-8adc15e2d0f5', name='红方-反舰巡逻-WP2', lat=27.152549, lon=124.765309, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='b98ec46b-2950-513b-804b-00142d32b7f2', name='红方-反舰巡逻-WP3', lat=26.48592, lon=125.523862, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='671aea16-43b4-53cc-b298-8d3ee64afd41', name='红方-反舰巡逻-WP4', lat=27.152587, lon=126.282457, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'33d4a119-9e75-5551-a756-ba45928810b7', 'a19332b1-a2f2-5d58-98b5-8adc15e2d0f5', 'b98ec46b-2950-513b-804b-00142d32b7f2', '671aea16-43b4-53cc-b298-8d3ee64afd41'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='f5584f19-d68c-5038-af6d-8fc9ef30f27a', name='蓝方-反舰打击-WP1', lat=30.664749, lon=122.124705, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='16922c1e-b757-5e54-ad47-c2c79d2b85bc', name='蓝方-反舰打击-WP2', lat=30.081416, lon=121.460934, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='30b2df16-92ff-56e1-84f8-751325ca392a', name='蓝方-反舰打击-WP3', lat=29.498343, lon=122.124409, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='e06951be-b2ae-5164-a206-4c26a16f0fa3', name='蓝方-反舰打击-WP4', lat=30.081677, lon=122.78818, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰打击}, {patrolZone={'f5584f19-d68c-5038-af6d-8fc9ef30f27a', '16922c1e-b757-5e54-ad47-c2c79d2b85bc', '30b2df16-92ff-56e1-84f8-751325ca392a', 'e06951be-b2ae-5164-a206-4c26a16f0fa3'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 052D #1},%{U:红方 054A #2}', %{M:红方-反舰巡逻}, false)
AssignUnitListToMission('%{U:蓝方 福特级 #1},%{U:蓝方 伯克级 #2},%{U:蓝方 F-35C #3}', %{M:蓝方-反舰打击}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/东海反舰遭遇战-V12.scen')
