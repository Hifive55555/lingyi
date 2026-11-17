-- ============================================================
-- 想定：巴士海峡反潜封锁
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:50:43
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-巴士海峡反潜封锁.scen
-- 规模：单元 4 型 / 6 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='巴士海峡反潜封锁', DURATION=14400, COMPLEXITY=2, DIFFICULTY=2, SEED=88097, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuW3tOWjq+a1t+WzoeWPjea9nOWwgemUgTwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5be05aOr5rW35bOh5Y+N5r2c5bCB6ZSBPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgNCDmnIggMTIg5pelIDA2IOaXtu+8jOW3tOWjq+a1t+WzoeOAguiTneaWueaguOa9nOiJhyAyIOiJmOW8l+WQieWwvOS6mue6p+S7juS4nOWNlyA5MCDmtbfph4zpmpDolL3mjqXov5HvvIw8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuWPpuaciSAxIOaetiBQLTNDIOWPjea9nOW3oemAu+acuu+8m+e6ouaWuSAyIOiJmCAwNTRB44CBMSDoiZggMDUyRCDlnKjopb/ljJcgMTAwIOa1t+mHjOWxleW8gO+8jOaJp+ihjOWPjea9nOW3oemAu++8jDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5beh6YC75Y2K5b6EIDM1IOa1t+mHjOOAgua1t+WGtSA1IOe6p++8jOS6kemHjyAwLjjvvIzpmY3pm6ggMjDjgILmjIHnu60gNCDlsI/ml7bjgII8L1NQQU4+PC9QPjwvQk9EWT4='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=120.9356, CAMERALAT=21.5589, CAMERAALT=747124.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=120.9356, CAMERALAT=21.5589, CAMERAALT=747124.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 20, 0.8, 5)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:蓝方}, type='Submarine', DATASOURCE=0.0, name='蓝方 弗吉尼亚 #1', dbid=553.0, latitude='20.439340', longitude='122.139983', heading=225, count=2.0})
U_2 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 P-3C #2', dbid=350.0, latitude='20.450961', longitude='122.281733', alt=8000.0, heading=225, loadoutid=3.0})
U_3 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #1', dbid=1965.0, latitude='22.678511', longitude='119.733352', heading=45, count=2.0})
U_4 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #2', dbid=2296.0, latitude='22.666890', longitude='119.589396', heading=45})

-- [6] 创建任务
-- 红方-反潜巡逻（Patrol/SUB=反潜）
M_1 = AddMission(%{S:红方}, '红方-反潜巡逻', 'Patrol', {isactive=true, type='SUB', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-防空巡逻（Patrol/AAW=防空）
M_2 = AddMission(%{S:蓝方}, '蓝方-防空巡逻', 'Patrol', {isactive=true, type='AAW', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-反潜巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='2e1932a0-4aaa-532a-8539-4c6691539103', name='红方-反潜巡逻-WP1', lat=23.085179, lon=120.108398, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='be21457a-84de-5b50-88fe-5eac6cb90202', name='红方-反潜巡逻-WP2', lat=22.260222, lon=120.108398, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='7365f7a2-c4af-5846-83a3-767245d7f224', name='红方-反潜巡逻-WP3', lat=22.260222, lon=119.21435, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='d1b0b665-9135-5276-9108-64c2d4779d4f', name='红方-反潜巡逻-WP4', lat=23.085179, lon=119.21435, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反潜巡逻}, {patrolZone={'2e1932a0-4aaa-532a-8539-4c6691539103', 'be21457a-84de-5b50-88fe-5eac6cb90202', '7365f7a2-c4af-5846-83a3-767245d7f224', 'd1b0b665-9135-5276-9108-64c2d4779d4f'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-防空巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='3d6a5b32-e7da-5cc2-8a6a-20c10e9d5166', name='蓝方-防空巡逻-WP1', lat=20.857629, lon=122.651067, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='dbbc6ec2-b2be-5dda-b927-46191a2cd044', name='蓝方-防空巡逻-WP2', lat=20.032672, lon=122.651067, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='0a24d629-3716-570b-bc65-6ac4c8971a3f', name='蓝方-防空巡逻-WP3', lat=20.032672, lon=121.770649, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='e858db92-d2d0-5e7e-9e75-0d2329a2f599', name='蓝方-防空巡逻-WP4', lat=20.857629, lon=121.770649, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-防空巡逻}, {patrolZone={'3d6a5b32-e7da-5cc2-8a6a-20c10e9d5166', 'dbbc6ec2-b2be-5dda-b927-46191a2cd044', '0a24d629-3716-570b-bc65-6ac4c8971a3f', 'e858db92-d2d0-5e7e-9e75-0d2329a2f599'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 054A #1},%{U:红方 052D #2}', %{M:红方-反潜巡逻}, false)
AssignUnitListToMission('%{U:蓝方 弗吉尼亚 #1},%{U:蓝方 P-3C #2}', %{M:蓝方-防空巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-巴士海峡反潜封锁.scen')
