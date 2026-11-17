-- ============================================================
-- 想定：台海联合火力打击
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:53:14
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-台海联合火力打击.scen
-- 规模：单元 7 型 / 10 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='台海联合火力打击', DURATION=7200, COMPLEXITY=2, DIFFICULTY=2, SEED=47406, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuWPsOa1t+iBlOWQiOeBq+WKm+aJk+WHuzwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5Y+w5rW36IGU5ZCI54Gr5Yqb5omT5Ye7PC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgNiDmnIggOCDml6UgMjIg5pe277yM5Y+w5rm+5rW35bOh44CC57qi5pa5IDIg6ImYIDA1MkRM44CBMSDoiZggMDU1IOWcqOa1t+Wzoeilv+S+pyA4MCDmtbfph4zvvIw8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPuWPpuacieWyuOWfuiBTLTQwMCDokKXkvY3kuo7ljJfnuqwgMjQuNDgg5bqm44CB5Lic57uPIDExOC4wOCDluqbvvIwyIOS4quWyuOiIsOWvvOW8ueiQpeS9jeS6juWMl+e6rCAyMy45MCDluqbjgIHkuJznu48gMTE3LjcwIOW6pu+8mzwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+6JOd5pa5IDEg6ImY5Lyv5YWL57qn5Zyo5YyX57qsIDI0LjYwIOW6puOAgeS4nOe7jyAxMjIuMTAg5bqm77yM5py65Zy6IDEg5bqn5L2N5LqO5YyX57qsIDI0LjAyIOW6puOAgeS4nOe7jyAxMjEuNjIg5bqm77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj4yIOaetiBGLTE2IOS7juivpeacuuWcuui1t+mjnuOAgue6ouaWueaJp+ihjOWvueWcsOaJk+WHu+S7u+WKoe+8jOW3oemAu+WNiuW+hCAzMCDmtbfph4zjgILmtbflhrUgMyDnuqfjgILmjIHnu60gMiDlsI/ml7bjgII8L1NQQU4+PC9QPjwvQk9EWT4='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=120.0433, CAMERALAT=24.2712, CAMERAALT=1274791.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=120.0433, CAMERALAT=24.2712, CAMERAALT=1274791.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.0, 3)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052DL #1', dbid=3586.0, latitude='24.530000', longitude='118.080000', heading=45, count=2.0})
U_2 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 055 #2', dbid=2834.0, latitude='24.449245', longitude='117.984806', heading=45})
U_3 = AddUnit({side=%{S:红方}, type='Facility', DATASOURCE=0.0, name='红方 S-400 #3', dbid=2029.0, latitude='24.480000', longitude='118.080000', heading=45})
U_4 = AddUnit({side=%{S:红方}, type='Facility', DATASOURCE=0.0, name='红方 岸舰导弹营 #4', dbid=3177.0, latitude='23.942426', longitude='117.746405', heading=45, count=2.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #1', dbid=112.0, latitude='24.600000', longitude='122.100000', heading=225})
U_6 = AddUnit({side=%{S:蓝方}, type='Facility', DATASOURCE=0.0, name='蓝方 机场 #2', dbid=430.0, latitude='24.020000', longitude='121.620000', heading=225})
U_7 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='蓝方 F-16 #3', dbid=4912.0, latitude='24.447046', longitude='122.340246', alt=8000.0, heading=225, loadoutid=9481.0, count=2.0})

-- [6] 创建任务
-- 红方-对地打击（Patrol/LAND=对地）
M_1 = AddMission(%{S:红方}, '红方-对地打击', 'Patrol', {isactive=true, type='LAND', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰巡逻（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:蓝方}, '蓝方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-对地打击 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='2c44fcd3-0e15-5398-b23e-85c3f691cf40', name='红方-对地打击-WP1', lat=24.685648, lon=118.336534, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='0bd3d79a-0cd4-5df8-8e97-c5e0b1cdbb6e', name='红方-对地打击-WP2', lat=23.978541, lon=118.336534, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='1591ba5a-e9f7-5330-8976-8692544c939a', name='红方-对地打击-WP3', lat=23.978541, lon=117.560493, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='fc663e2e-87e8-5026-b19e-5e09b9d14a4e', name='红方-对地打击-WP4', lat=24.685648, lon=117.560493, highlighted=true})
SetMission(%{S:红方}, %{M:红方-对地打击}, {patrolZone={'2c44fcd3-0e15-5398-b23e-85c3f691cf40', '0bd3d79a-0cd4-5df8-8e97-c5e0b1cdbb6e', '1591ba5a-e9f7-5330-8976-8692544c939a', 'fc663e2e-87e8-5026-b19e-5e09b9d14a4e'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='2cf77aff-f029-54d2-8616-5b1960f1b61c', name='蓝方-反舰巡逻-WP1', lat=24.768161, lon=122.472857, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='1a2dff0c-1f81-5974-a474-7880a251ebe3', name='蓝方-反舰巡逻-WP2', lat=23.943203, lon=122.472857, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='213a89f7-f924-57c0-8c68-ee2a584a9245', name='蓝方-反舰巡逻-WP3', lat=23.943203, lon=121.567307, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='4175a1eb-ef69-5d18-8caf-18d299a2ed4b', name='蓝方-反舰巡逻-WP4', lat=24.768161, lon=121.567307, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰巡逻}, {patrolZone={'2cf77aff-f029-54d2-8616-5b1960f1b61c', '1a2dff0c-1f81-5974-a474-7880a251ebe3', '213a89f7-f924-57c0-8c68-ee2a584a9245', '4175a1eb-ef69-5d18-8caf-18d299a2ed4b'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 052DL #1},%{U:红方 055 #2},%{U:红方 S-400 #3},%{U:红方 岸舰导弹营 #4}', %{M:红方-对地打击}, false)
AssignUnitListToMission('%{U:蓝方 伯克级 #1},%{U:蓝方 机场 #2},%{U:蓝方 F-16 #3}', %{M:蓝方-反舰巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-台海联合火力打击.scen')
