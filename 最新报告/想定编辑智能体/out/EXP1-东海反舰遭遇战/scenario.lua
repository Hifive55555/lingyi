-- ============================================================
-- 想定：东海反舰遭遇战
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:49:25
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-东海反舰遭遇战.scen
-- 规模：单元 5 型 / 10 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='东海反舰遭遇战', DURATION=10800, COMPLEXITY=2, DIFFICULTY=2, SEED=98863, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuS4nOa1t+WPjeiIsOmBremBh+aImDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5Lic5rW35Y+N6Iiw6YGt6YGH5oiYPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgMyDmnIggMSDml6XkuIrljYggOCDml7bvvIzkuJzmtbfkuK3pg6jjgILnuqLmlrkgMiDoiZggMDUyROOAgTEg6ImYIDA1NEEg5LuO6KW/5L6nIDExMCDmtbfph4zov5vlhaXvvIw8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuaJp+ihjOWPjeiIsOW3oemAu++8jOW3oemAu+WNiuW+hCA0MCDmtbfph4zvvJvok53mlrkgMSDkuKroiKrmr43miZPlh7vnvqTvvIwxIOiJmOemj+eJuee6p+OAgTIg6ImY5Lyv5YWL57qn5Zyo5Lic5L6nIDEzMCDmtbfph4zvvIw8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPjQg5p62IEYtMzVDIOaJp+ihjOWPjeiIsOaJk+WHu+OAgua1t+WGtSA0IOe6p++8jOS6kemHjyAwLjbjgILmjIHnu60gMyDlsI/ml7bjgILlj4zmlrnoh6rnlLHlvIDngavjgII8L1NQQU4+PC9QPjwvQk9EWT4='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=124.2384, CAMERALAT=28.4293, CAMERAALT=1373979.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=124.2384, CAMERALAT=28.4293, CAMERAALT=1373979.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.6, 4)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #1', dbid=2296.0, latitude='28.500000', longitude='121.913863', heading=45, count=2.0})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #2', dbid=1965.0, latitude='28.488379', longitude='121.762721', heading=45})
U_3 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 福特级 #1', dbid=506.0, latitude='28.500000', longitude='126.465435', heading=225})
U_4 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #2', dbid=112.0, latitude='28.511621', longitude='126.616577', heading=225, count=2.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F-35C #3', dbid=824.0, latitude='28.347046', longitude='126.713997', alt=8000.0, heading=225, loadoutid=3004.0, count=4.0})

-- [6] 创建任务
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_1 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:蓝方}, '蓝方-反舰打击', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='b7a22e5e-a689-5f31-b266-915bdc97a3a0', name='红方-反舰巡逻-WP1', lat=28.965594, lon=122.37467, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='5fbd47e6-8257-5ce7-b986-d914ea2cae89', name='红方-反舰巡逻-WP2', lat=28.022785, lon=122.37467, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='ccaf8c44-2f8e-5f47-93f0-1f5adb0c3b6b', name='红方-反舰巡逻-WP3', lat=28.022785, lon=121.301914, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='459fe4a2-928a-5fc0-a684-db07585cf552', name='红方-反舰巡逻-WP4', lat=28.965594, lon=121.301914, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'b7a22e5e-a689-5f31-b266-915bdc97a3a0', '5fbd47e6-8257-5ce7-b986-d914ea2cae89', 'ccaf8c44-2f8e-5f47-93f0-1f5adb0c3b6b', '459fe4a2-928a-5fc0-a684-db07585cf552'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='c67092ac-b6ad-532a-9e6c-560f707b4715', name='蓝方-反舰打击-WP1', lat=28.865368, lon=127.067817, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='3e867038-131f-57f8-82be-836bc3e60777', name='蓝方-反舰打击-WP2', lat=28.04041, lon=127.067817, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='cfdcf327-2aac-56da-b811-4f61e89ce7de', name='蓝方-反舰打击-WP3', lat=28.04041, lon=126.129522, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='2e1f700f-5734-5282-a95e-1bade3a4242e', name='蓝方-反舰打击-WP4', lat=28.865368, lon=126.129522, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰打击}, {patrolZone={'c67092ac-b6ad-532a-9e6c-560f707b4715', '3e867038-131f-57f8-82be-836bc3e60777', 'cfdcf327-2aac-56da-b811-4f61e89ce7de', '2e1f700f-5734-5282-a95e-1bade3a4242e'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 052D #1},%{U:红方 054A #2}', %{M:红方-反舰巡逻}, false)
AssignUnitListToMission('%{U:蓝方 福特级 #1},%{U:蓝方 伯克级 #2},%{U:蓝方 F-35C #3}', %{M:蓝方-反舰打击}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-东海反舰遭遇战.scen')
