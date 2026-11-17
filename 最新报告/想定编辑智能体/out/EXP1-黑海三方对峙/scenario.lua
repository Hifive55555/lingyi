-- ============================================================
-- 想定：黑海三方对峙
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:54:34
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-黑海三方对峙.scen
-- 规模：单元 3 型 / 3 个；任务 3 个；参考点 12 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='黑海三方对峙', DURATION=10800, COMPLEXITY=2, DIFFICULTY=2, SEED=60640, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPum7kea1t+S4ieaWueWvueWzmTwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya6buR5rW35LiJ5pa55a+55bOZPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgNyDmnIggMyDml6UgMDkg5pe277yM6buR5rW36KW/6YOo44CC57qi5pa5IDEg6ImYIDA1MkQg5LuO5YyX5L6nIDkwIOa1t+mHjOWNl+S4i++8jDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+6JOd5pa5IDEg6ImY5Lyv5YWL57qn5LuO5Y2X5L6nIDEwMCDmtbfph4zljJfkuIrvvIzlj4vmlrkgMSDoiZjooaXnu5noiLDlnKjkuJzkvqcgMTIwIOa1t+mHjOOAgjwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+57qi6JOd5Y+M5pa55pWM5a+577yM5Y+L5pa55LiO57qi5pa55Y+L5aW944CB5LiO6JOd5pa55Lit56uL44CC57qi5pa55omn6KGM5Y+N6Iiw5beh6YC777yM5Y2K5b6EIDMwIOa1t+mHjOOAgjwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5rW35Ya1IDQg57qn77yM5LqR6YePIDAuNeOAguaMgee7rSAzIOWwj+aXtuOAgjwvU1BBTj48L1A+PC9CT0RZPg=='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})
S_3 = AddSide({side='友方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'N')
SetSidePosture(%{S:红方}, %{S:友方}, 'N')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'N')
SetSidePosture(%{S:蓝方}, %{S:友方}, 'N')
SetSidePosture(%{S:友方}, %{S:红方}, 'N')
SetSidePosture(%{S:友方}, %{S:蓝方}, 'N')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=35.1826, CAMERALAT=43.4593, CAMERAALT=873894.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=35.1826, CAMERALAT=43.4593, CAMERAALT=873894.0})
SetSideOptions({side=%{S:友方}, CAMERALON=35.1826, CAMERALAT=43.4593, CAMERAALT=873894.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:友方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.5, 4)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 052D #1', dbid=2296.0, latitude='44.885195', longitude='33.608031', heading=45})
U_2 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #1', dbid=112.0, latitude='42.033333', longitude='34.000000', heading=225})
U_3 = AddUnit({side=%{S:友方}, type='Ship', DATASOURCE=0.0, name='友方 补给舰 #1', dbid=2980.0, latitude='43.500000', longitude='36.757197', heading=45})

-- [6] 创建任务
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_1 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰巡逻（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:蓝方}, '蓝方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 友方-反舰巡逻（Patrol/NAVAL=反舰）
M_3 = AddMission(%{S:友方}, '友方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='f899a10e-8c34-5511-8280-b161b1d56945', name='红方-反舰巡逻-WP1', lat=45.353553, lon=34.5, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='770302d8-8594-5fc5-90d3-caa487073d01', name='红方-反舰巡逻-WP2', lat=44.646447, lon=34.5, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='7f73426a-b9d4-5440-9c56-5554297b5cc2', name='红方-反舰巡逻-WP3', lat=44.646447, lon=33.5, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='1783915e-e74c-5c90-ace9-a814ee14ab60', name='红方-反舰巡逻-WP4', lat=45.353553, lon=33.5, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'f899a10e-8c34-5511-8280-b161b1d56945', '770302d8-8594-5fc5-90d3-caa487073d01', '7f73426a-b9d4-5440-9c56-5554297b5cc2', '1783915e-e74c-5c90-ace9-a814ee14ab60'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 蓝方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='0b5a54d5-22f7-5236-8295-a29e20253029', name='蓝方-反舰巡逻-WP1', lat=42.245812, lon=34.553598, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='eb176cef-fe68-52ac-867a-873e23ac3672', name='蓝方-反舰巡逻-WP2', lat=41.420854, lon=34.553598, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='e671fd0b-24ce-5993-8606-1c4fd61fd861', name='蓝方-反舰巡逻-WP3', lat=41.420854, lon=33.446402, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='96d61032-0865-5f8f-8ea6-e1c03d5fdfc0', name='蓝方-反舰巡逻-WP4', lat=42.245812, lon=33.446402, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反舰巡逻}, {patrolZone={'0b5a54d5-22f7-5236-8295-a29e20253029', 'eb176cef-fe68-52ac-867a-873e23ac3672', 'e671fd0b-24ce-5993-8606-1c4fd61fd861', '96d61032-0865-5f8f-8ea6-e1c03d5fdfc0'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 友方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:友方}, guid='b1129a98-cec3-51c9-8986-5ebdd4383a3c', name='友方-反舰巡逻-WP1', lat=43.912479, lon=37.32584, highlighted=true})
AddReferencePoint({side=%{S:友方}, guid='7a19dff4-53d2-55fb-a03a-9dda671d8f60', name='友方-反舰巡逻-WP2', lat=43.087521, lon=37.32584, highlighted=true})
AddReferencePoint({side=%{S:友方}, guid='6eda7d0a-c2ec-5a1c-86d1-c12aac865319', name='友方-反舰巡逻-WP3', lat=43.087521, lon=36.188554, highlighted=true})
AddReferencePoint({side=%{S:友方}, guid='2af9d7f6-2679-5575-a515-41be23f57c89', name='友方-反舰巡逻-WP4', lat=43.912479, lon=36.188554, highlighted=true})
SetMission(%{S:友方}, %{M:友方-反舰巡逻}, {patrolZone={'b1129a98-cec3-51c9-8986-5ebdd4383a3c', '7a19dff4-53d2-55fb-a03a-9dda671d8f60', '6eda7d0a-c2ec-5a1c-86d1-c12aac865319', '2af9d7f6-2679-5575-a515-41be23f57c89'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:红方 052D #1}', %{M:红方-反舰巡逻}, false)
AssignUnitListToMission('%{U:蓝方 伯克级 #1}', %{M:蓝方-反舰巡逻}, false)
AssignUnitListToMission('%{U:友方 补给舰 #1}', %{M:友方-反舰巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-黑海三方对峙.scen')
