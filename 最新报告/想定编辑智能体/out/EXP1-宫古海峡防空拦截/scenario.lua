-- ============================================================
-- 想定：宫古海峡防空拦截
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:51:57
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-宫古海峡防空拦截.scen
-- 规模：单元 5 型 / 13 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='宫古海峡防空拦截', DURATION=7200, COMPLEXITY=2, DIFFICULTY=2, SEED=30354, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuWuq+WPpOa1t+WzoemYsuepuuaLpuaIqjwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5a6r5Y+k5rW35bOh6Ziy56m65oum5oiqPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgNSDmnIggMjAg5pelIDE0IOaXtu+8jOWuq+WPpOa1t+WzoeOAgue6ouaWuSA0IOaetuatvC0yMOOAgTIg5p625q28LTE2IOS7juilv+WMlyAxMjAg5rW36YeM6LW36aOe77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7pq5jluqYgOTAwMCDnsbPvvIzmiafooYzpmLLnqbrlt6HpgLvvvIzlt6HpgLvljYrlvoQgNDUg5rW36YeM77yM5bm26YWN5aSHIDEg5p6256m66K2mLTUwMCDpooTorabmnLrvvJs8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuiTneaWuSA0IOaetiBGLTM1QeOAgTIg5p62IEVBLTE4RyDku47kuJzljZcgMTQwIOa1t+mHjOi/m+WFpe+8jOmrmOW6piAxMDAwMCDnsbPjgILmjIHnu60gMiDlsI/ml7bjgILosKjmhY7lvIDngavjgII8L1NQQU4+PC9QPjwvQk9EWT4='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=125.5803, CAMERALAT=24.7586, CAMERAALT=1044332.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=125.5803, CAMERALAT=24.7586, CAMERAALT=1044332.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='红方 歼-20 #1', dbid=2463.0, latitude='26.214214', longitude='123.942114', alt=8000.0, heading=45, loadoutid=3.0, count=4.0})
U_2 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='红方 歼-16 #2', dbid=2853.0, latitude='26.202593', longitude='123.794061', alt=8000.0, heading=45, loadoutid=3.0, count=2.0})
U_3 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='红方 空警-500 #3', dbid=3683.0, latitude='26.367168', longitude='123.698631', alt=9000.0, heading=45, loadoutid=3.0})
U_4 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F-35A #1', dbid=278.0, latitude='23.150084', longitude='127.317533', alt=10000.0, heading=225, loadoutid=11128.0, count=4.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 EA-18G #2', dbid=343.0, latitude='23.161705', longitude='127.461991', alt=10000.0, heading=225, loadoutid=3091.0, count=2.0})

-- [6] 创建任务
-- 红方-防空巡逻（Patrol/AAW=防空）
M_1 = AddMission(%{S:红方}, '红方-防空巡逻', 'Patrol', {isactive=true, type='AAW', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-防空巡逻（Patrol/AAW=防空）
M_2 = AddMission(%{S:蓝方}, '蓝方-防空巡逻', 'Patrol', {isactive=true, type='AAW', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-防空巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='756d0d67-0a35-52af-ae56-737db98e44a0', name='红方-防空巡逻-WP1', lat=26.791655, lon=124.40297, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='526cc5ad-b29f-5daa-9afe-18057a6b5b06', name='红方-防空巡逻-WP2', lat=25.730995, lon=124.40297, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='0ee06974-abb3-5813-9bd3-0c2af2d916b3', name='红方-防空巡逻-WP3', lat=25.730995, lon=123.220234, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='85419b3c-ede2-5a9a-8638-3ce0ca5f4f82', name='红方-防空巡逻-WP4', lat=26.791655, lon=123.220234, highlighted=true})
SetMission(%{S:红方}, %{M:红方-防空巡逻}, {patrolZone={'756d0d67-0a35-52af-ae56-737db98e44a0', '526cc5ad-b29f-5daa-9afe-18057a6b5b06', '0ee06974-abb3-5813-9bd3-0c2af2d916b3', '85419b3c-ede2-5a9a-8638-3ce0ca5f4f82'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-防空巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='b9f73d98-721c-5440-9b0b-cf28ba41d7f4', name='蓝方-防空巡逻-WP1', lat=23.568373, lon=127.838383, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='e7ec4e84-9200-5199-8f07-000db98b3dc6', name='蓝方-防空巡逻-WP2', lat=22.743416, lon=127.838383, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='816edcd7-f016-5b99-9f68-961db690cd79', name='蓝方-防空巡逻-WP3', lat=22.743416, lon=126.941141, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='3662a6d8-3e0b-593a-a0d8-ee03e71a1782', name='蓝方-防空巡逻-WP4', lat=23.568373, lon=126.941141, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-防空巡逻}, {patrolZone={'b9f73d98-721c-5440-9b0b-cf28ba41d7f4', 'e7ec4e84-9200-5199-8f07-000db98b3dc6', '816edcd7-f016-5b99-9f68-961db690cd79', '3662a6d8-3e0b-593a-a0d8-ee03e71a1782'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 歼-20 #1},%{U:红方 歼-16 #2},%{U:红方 空警-500 #3}', %{M:红方-防空巡逻}, false)
AssignUnitListToMission('%{U:蓝方 F-35A #1},%{U:蓝方 EA-18G #2}', %{M:蓝方-防空巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-宫古海峡防空拦截.scen')
