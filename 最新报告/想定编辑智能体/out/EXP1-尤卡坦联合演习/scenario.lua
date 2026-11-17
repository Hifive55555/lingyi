-- ============================================================
-- 想定：尤卡坦联合演习
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 20:57:07
-- 保存路径：D:/LingYi/Data/Scenarios/EXP1-尤卡坦联合演习.scen
-- 规模：单元 2 型 / 4 个；任务 2 个；参考点 8 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='尤卡坦联合演习', DURATION=7200, COMPLEXITY=2, DIFFICULTY=2, SEED=26697, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPuWwpOWNoeWdpuiBlOWQiOa8lOS5oDwvU1BBTj48L1A+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiPjxTUEFOIHN0eWxlPSJGT05ULVNJWkU6IDE0cHQ7IEZPTlQtRkFNSUxZOiAn5a6L5L2TJyI+5qCH6aKY77ya5bCk5Y2h5Z2m6IGU5ZCI5ryU5LmgPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7orr7lrpogMjAyNiDlubQgOSDmnIggMTAg5pelIDEwIOaXtu+8jOWwpOWNoeWdpuOAgue6ouaWuSAyIOiJmCAwNTRBIOWcqOilv+S+pyA4MCDmtbfph4zvvIzok53mlrkgMiDoiZjkvK/lhYvnuqflnKjkuJzkvqcgOTAg5rW36YeM77yMPC9TUEFOPjwvUD48UCBzdHlsZT0iTUFSR0lOOiAxMnB4IDBweCI+PFNQQU4gc3R5bGU9IkZPTlQtU0laRTogMTRwdDsgRk9OVC1GQU1JTFk6ICflrovkvZMnIj7lj4zmlrnlj4vlpb3vvIzov5vooYzogZTlkIjmvJTkuaDvvIzlkITmiafooYzlj43mvZzlt6HpgLvvvIzlt6HpgLvljYrlvoQgMjUg5rW36YeM44CC5rW35Ya1IDIg57qn77yM5LqR6YePIDAuM+OAguaMgee7rSAyIOWwj+aXtuOAgjwvU1BBTj48L1A+PC9CT0RZPg=='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'F')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'F')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=-87.9104, CAMERALAT=21.5, CAMERAALT=845050.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=-87.9104, CAMERALAT=21.5, CAMERAALT=845050.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(20, 0, 0.3, 2)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='红方 054A #1', dbid=1965.0, latitude='21.500000', longitude='-89.433048', heading=45, count=2.0})
U_2 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='蓝方 伯克级 #1', dbid=112.0, latitude='21.500000', longitude='-86.387821', heading=225, count=2.0})

-- [6] 创建任务
-- 蓝方-反潜巡逻（Patrol/SUB=反潜）
M_1 = AddMission(%{S:蓝方}, '蓝方-反潜巡逻', 'Patrol', {isactive=true, type='SUB', unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-反舰巡逻（Patrol/NAVAL=反舰）
M_2 = AddMission(%{S:红方}, '红方-反舰巡逻', 'Patrol', {isactive=true, type='NAVAL', unloadMountDBID=0.0, unloadMountCount=0.0})

-- [7] 参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）
-- 蓝方-反潜巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:蓝方}, guid='0fbc5361-942a-5233-9a76-9158cbab92fe', name='蓝方-反潜巡逻-WP1', lat=21.794628, lon=-86.071159, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='0f7d2b76-1497-5372-a1c7-e65783124233', name='蓝方-反潜巡逻-WP2', lat=21.205372, lon=-86.071159, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='8f6054f7-cf81-564c-a1ab-2415e2fbaf81', name='蓝方-反潜巡逻-WP3', lat=21.205372, lon=-86.704483, highlighted=true})
AddReferencePoint({side=%{S:蓝方}, guid='6ea2422b-2581-5644-a9a2-8612bddb1667', name='蓝方-反潜巡逻-WP4', lat=21.794628, lon=-86.704483, highlighted=true})
SetMission(%{S:蓝方}, %{M:蓝方-反潜巡逻}, {patrolZone={'0fbc5361-942a-5233-9a76-9158cbab92fe', '0f7d2b76-1497-5372-a1c7-e65783124233', '8f6054f7-cf81-564c-a1ab-2415e2fbaf81', '6ea2422b-2581-5644-a9a2-8612bddb1667'}, unloadMountDBID=0.0, unloadMountCount=0.0})
-- 红方-反舰巡逻 的巡逻区参考点（GUID 由生成端确定性给出）
AddReferencePoint({side=%{S:红方}, guid='e7246b9b-3206-54de-acda-4b3672935d66', name='红方-反舰巡逻-WP1', lat=21.912479, lon=-88.989721, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='6aff58bb-9d6b-5cb7-ba20-c33635842fdc', name='红方-反舰巡逻-WP2', lat=21.087521, lon=-88.989721, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='e83abd15-72c1-5673-8059-8c59ceb53089', name='红方-反舰巡逻-WP3', lat=21.087521, lon=-89.876375, highlighted=true})
AddReferencePoint({side=%{S:红方}, guid='146f1e44-4f87-585a-9e4a-a50139709907', name='红方-反舰巡逻-WP4', lat=21.912479, lon=-89.876375, highlighted=true})
SetMission(%{S:红方}, %{M:红方-反舰巡逻}, {patrolZone={'e7246b9b-3206-54de-acda-4b3672935d66', '6aff58bb-9d6b-5cb7-ba20-c33635842fdc', 'e83abd15-72c1-5673-8059-8c59ceb53089', '146f1e44-4f87-585a-9e4a-a50139709907'}, unloadMountDBID=0.0, unloadMountCount=0.0})

-- [8] 单元-任务分配
-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给
AssignUnitListToMission('%{U:蓝方 伯克级 #1}', %{M:蓝方-反潜巡逻}, false)
AssignUnitListToMission('%{U:红方 054A #1}', %{M:红方-反舰巡逻}, false)

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-尤卡坦联合演习.scen')
