# 做成 Windows 安装包（Inno Setup）

## 你需要做的（一次性，5 分钟）

在**装了 Inno Setup 6 的那台 Windows** 上：

1. 把 `pack.sh` / `pack.py` 打出来的 zip 拷过去，解压；
2. 双击 `installer\build_installer.bat`；
3. 产物：`dist\灵弈小窗+红方智能体_setup_20261119.exe`（约 1 MB）。

拿到比赛机上**双击安装**（不要"以管理员身份运行"），向导里只需确认灵弈根目录
（默认 `D:\LingYi`，会自动探测），点安装 → 它会调 `deploy.ps1` 完成
"备份 + 拷贝 + `check_env.py` 自检"，最后可选创建桌面快捷方式。

## 它到底做了什么

| 阶段 | 动作 |
| --- | --- |
| 打包 | `pack.py --no-zip --name _pkg` → `build\_pkg\`（与 zip 同一套清单，缺 `wv2\overlay_wv2.exe` 会直接失败） |
| 编译 | 找 `ISCC.exe`（`C:\Program Files (x86)\Inno Setup 6\`，或查注册表）→ 编译 `setup.iss` |
| 安装 | 整包解到 `{灵弈}\_pkg\`，然后 `[Run]` 调 `_pkg\deploy.ps1 -Lingyi {灵弈}` |
| 收尾 | 桌面/开始菜单快捷方式：`灵弈小窗`、`小窗截图`、`打开小窗日志目录`；装完提示"立刻打开小窗" |

## 为什么不是"传统安装包"

- **必须普通权限**（`PrivilegesRequired=lowest`）：比赛机 `C:\Users\A\AppData\Local`
  不可写，管理员（高完整性级别）跑会让 WebView2 拿不到 profile 目录 → 小窗灰屏
  + `0x80070005`。所以安装程序不写注册表、不装服务、不要求 UAC 提权。
- **不复制第二套逻辑**：落点映射只写在 `deploy.ps1` 里，安装包只是"解包 + 调它"，
  这样手工部署和安装包部署永远一致，也自动获得 `.bak_时间戳` 备份和自检。
- **卸载只删自己**：`[UninstallDelete]` 只清 `{灵弈}\_pkg`，灵弈本体、日志、
  比赛数据一律不动（覆盖过的文件保留 `.bak_*` 备份）。

## 没有 Inno Setup 怎么办

- 直接解压 zip → 双击 `deploy.bat`，功能完全一样（安装包只是把它包了一层）；
- 或者在 Inno Setup 图形界面里打开 `setup.iss` 按 `Ctrl+F9` 编译（先跑一次
  `pack.py --no-zip --name _pkg --out build` 把 `build\_pkg` 备好）；
- 想在 Linux 上出 `setup.exe`：需要 wine + Inno Setup（不推荐，容易踩字体/编码坑）。

## 编译报错怎么办

| 报错 | 处理 |
| --- | --- |
| `ArchitecturesAllowed` / `ArchitecturesInstallIn64BitMode` 值无法识别 | 老/新版本 Inno 对这些值的叫法不同：把 `setup.iss` 里两行改成 `x64compatible` 或者直接删掉这两行 |
| 找不到 `build\_pkg` | 先手工跑一次 `python pack.py --no-zip --name _pkg --out build`（在包目录下） |
| 中文变成乱码 | `setup.iss` 必须存成 **UTF-8 带 BOM**；用 VS Code 另存为 "UTF-8 with BOM" |
| 提示 `ChineseSimplified.isl` 不存在 | 本脚本没有引用它（Inno 6 默认不带），不要加中文语言文件 |

## 已知限制

- 只支持 64 位 Windows（`ArchitecturesAllowed=x64`），与 WebView2 宿主的 `/platform:x64` 一致；
- 安装包不含 `entitys` 平台库（用灵弈自带的），要带就先用 `pack.py --with-entitys` 打包再编；
- 中文向导文本靠 `[Messages]` 覆盖（Inno 6 默认不带 `ChineseSimplified.isl`），
  按钮仍是英文（Next/Install/Finish），不影响使用。
