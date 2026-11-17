-- ============================================================
-- 想定：海洋空战-V02
-- 生成：sce_agent（想定编辑智能体）  2026-11-17 21:01:27
-- 保存路径：D:/LingYi/Data/Scenarios/海洋空战-V02.scen
-- 规模：单元 16 型 / 16 个；任务 0 个；参考点 0 个
-- ============================================================
-- [1] 新建空白想定 + 元信息（DESCRIPTION 是 Base64）
NewScenario('','')
SetScenarioInfo({TITLE='海洋空战-V02', DURATION=6000, COMPLEXITY=2, DIFFICULTY=2, SEED=48069, DESCRIPTION='PEJPRFkgc2Nyb2xsPWF1dG8+PFAgc3R5bGU9Ik1BUkdJTjogMTJweCAwcHgiIGFsaWduPWNlbnRlcj48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxOHB0OyBGT05ULUZBTUlMWTogJ+m7keS9kyciPua1t+a0i+epuuaImC1WMDI8L1NQQU4+PC9QPjxQIHN0eWxlPSJNQVJHSU46IDEycHggMHB4Ij48U1BBTiBzdHlsZT0iRk9OVC1TSVpFOiAxNHB0OyBGT05ULUZBTUlMWTogJ+Wui+S9kyciPueUseaXouacieaDs+WumuOAiua1t+a0i+epuuaImOOAi+e7k+aehOWkjeWIuzwvU1BBTj48L1A+PC9CT0RZPg=='})

-- [2] 添加推演方（AddSide 返回推演方 GUID）
S_1 = AddSide({side='红方'})
S_2 = AddSide({side='蓝方'})

-- [3] 对抗关系 / 视点 / 条令
-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）
SetSidePosture(%{S:红方}, %{S:蓝方}, 'H')
SetSidePosture(%{S:蓝方}, %{S:红方}, 'H')
-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）
SetSideOptions({side=%{S:红方}, CAMERALON=79.8865, CAMERALAT=12.9661, CAMERAALT=44337001.0})
SetSideOptions({side=%{S:蓝方}, CAMERALON=79.8865, CAMERALAT=12.9661, CAMERAALT=44337001.0})
-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）
SetDoctrine({side=%{S:红方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})
SetDoctrine({side=%{S:蓝方}}, {WCS_Air='1', WCS_Surface='1', WCS_Submarine='1', WCS_Land='1', Nukes='0', BTAT='2', BingoJokerRTB='2', WinchesterShotgunRTB='1', AE='1', MS='1'})

-- [4] 气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)
SetWeather(15, 0, 0.0, 0)

-- [5] 部署单元
-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）
U_1 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='闪电 #2', dbid=3836.0, latitude='25.527906', longitude='153.254548', alt=10972.8, heading=0.0, loadoutid=3004.0})
U_9 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #1', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_12 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #4', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_8 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='闪电 #1', dbid=3836.0, latitude='25.932216', longitude='159.772978', alt=10972.8, heading=0.0, loadoutid=3004.0})
U_5 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='闪电 #4', dbid=3836.0, latitude='25.932216', longitude='159.772978', alt=10972.8, heading=0.0, loadoutid=3004.0})
U_10 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #2', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_11 = AddUnit({side=%{S:蓝方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #3', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_8 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='闪电 #1', dbid=3836.0, latitude='25.527906', longitude='153.254548', alt=10972.8, heading=0.0, loadoutid=3004.0})
U_9 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #1', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_10 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #2', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_11 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #3', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_12 = AddUnit({side=%{S:红方}, type='Aircraft', DATASOURCE=0.0, name='F/A-18E #4', dbid=753.0, latitude='0.000000', longitude='0.000000', alt=6.1, heading=0.0, loadoutid=4617.0})
U_14 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='CVN-78“杰拉德.R.福特”福特级号航空母舰', dbid=506.0, latitude='25.527906', longitude='153.254548', heading=0.0})
U_14 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='CVN-78“杰拉德.R.福特”福特级号航空母舰', dbid=506.0, latitude='25.932216', longitude='159.772978', heading=0.0})
U_16 = AddUnit({side=%{S:蓝方}, type='Ship', DATASOURCE=0.0, name='DDG 113“约翰.芬”阿里伯克级 Flight IIA导弹驱逐舰', dbid=2866.0, latitude='25.837252', longitude='157.506848', heading=0.0})
U_16 = AddUnit({side=%{S:红方}, type='Ship', DATASOURCE=0.0, name='DDG 113“约翰.芬”阿里伯克级 Flight IIA导弹驱逐舰', dbid=2866.0, latitude='25.798576', longitude='155.266136', heading=0.0})

-- [9] 保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）
Command_SaveScen('D:/LingYi/Data/Scenarios/海洋空战-V02.scen')
