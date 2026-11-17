-- ============================================================
-- 想定：东海反舰遭遇战-V05
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:38:43
-- 保存路径：D:/LingYi/Data/Scenarios/东海反舰遭遇战-V05.scen
-- 规模：单元 5 型 / 10 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='东海反舰遭遇战-V05', DURATION=10800, COMPLEXITY=2, DIFFICULTY=2, SEED=18043, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuS4nOa1t+WPjeiIsOmBremBh+aImC1WMDU8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuagh+mimO+8muS4nOa1t+WPjeiIsOmBremBh+aImDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+6K6+5a6aIDIwMjYg5bm0IDMg5pyIIDEg5pel5LiK5Y2IIDgg5pe277yM5Lic5rW35Lit6YOo44CC57qi5pa5IDIg6ImYIDA1MkTjgIExIOiJmCAwNTRBIOS7juilv+S+pyAxMTAg5rW36YeM6L+b5YWl77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7miafooYzlj43oiLDlt6HpgLvvvIzlt6HpgLvljYrlvoQgNDAg5rW36YeM77yb6JOd5pa5IDEg5Liq6Iiq5q+N5omT5Ye7576k77yMMSDoiZjnpo/nibnnuqfjgIEyIOiJmOS8r+WFi+e6p+WcqOS4nOS+pyAxMzAg5rW36YeM77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj40IOaetiBGLTM1QyDmiafooYzlj43oiLDmiZPlh7vjgILmtbflhrUgNCDnuqfvvIzkupHph48gMC4244CC5oyB57utIDMg5bCP5pe244CC5Y+M5pa56Ieq55Sx5byA54Gr44CCPC9TUEFOPjwvUD48L0JPRFk+'})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=123.7616, CAMERALAT=28.458, CAMERAALT=1373979.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=123.7616, CAMERALAT=28.458, CAMERAALT=1373979.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.6, 2)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #1', dbid=2296.0, latitude='28.500000', longitude='126.086137', heading=45.0, count=2.0})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #2', dbid=1965.0, latitude='28.488379', longitude='126.237279', heading=45.0})
U_3 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 福特级 #1', dbid=506.0, latitude='28.550000', longitude='121.534565', heading=225.0})
U_4 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #2', dbid=112.0, latitude='28.569024', longitude='121.541132', heading=225.0, count=2.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F-35C #3', dbid=824.0, latitude='28.347046', longitude='121.286003', alt=8000.0, heading=225.0, loadoutid=3004.0, count=4.0})

-- [6] 创建任务
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_1 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:蓝方}, '蓝方-反舰打击', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='967db7c7-3989-5a25-bd1e-c2ce3ddc2a0e', name='红方-反舰巡逻-WP1', lat=28.965594, lon=125.62533, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='371d1db8-1f84-57cc-8a5d-81eceb13b9c9', name='红方-反舰巡逻-WP2', lat=28.022785, lon=125.62533, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='2b4d2b38-862b-5f02-952e-f5cdfd788b20', name='红方-反舰巡逻-WP3', lat=28.022785, lon=126.698086, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='78186d51-5a64-5e20-a388-08e35e65c873', name='红方-反舰巡逻-WP4', lat=28.965594, lon=126.698086, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'967db7c7-3989-5a25-bd1e-c2ce3ddc2a0e', '371d1db8-1f84-57cc-8a5d-81eceb13b9c9', '2b4d2b38-862b-5f02-952e-f5cdfd788b20', '78186d51-5a64-5e20-a388-08e35e65c873'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='ff0d68f3-7d02-5e9b-9545-19b357d482be', name='蓝方-反舰打击-WP1', lat=28.865368, lon=120.932183, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='8636e499-837b-5da5-8d42-816764ee4022', name='蓝方-反舰打击-WP2', lat=28.04041, lon=120.932183, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='75828721-27e0-5d3a-bdb2-bd39e6d52c19', name='蓝方-反舰打击-WP3', lat=28.04041, lon=121.870478, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='620e08b6-5816-59a4-8dc6-d33b6a8ff804', name='蓝方-反舰打击-WP4', lat=28.865368, lon=121.870478, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰打击}, {patrolZone={'ff0d68f3-7d02-5e9b-9545-19b357d482be', '8636e499-837b-5da5-8d42-816764ee4022', '75828721-27e0-5d3a-bdb2-bd39e6d52c19', '620e08b6-5816-59a4-8dc6-d33b6a8ff804'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 052D #1},%{U:红方 054A #2}', %{M:红方-反舰巡逻}, false)
AssignUnitListToMission('%{U:蓝方 福特级 #1},%{U:蓝方 伯克级 #2},%{U:蓝方 F-35C #3}', %{M:蓝方-反舰打击}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/东海反舰遭遇战-V05.scen')
