# Keychron V1 Auto OS

公开项目名称：`keychron-v1-auto-os`。**目前仅适配 Keychron V1 ANSI 旋钮版**，不是全系列通用固件。

让 Keychron V1 在显示器 KVM 切换主机后自动选择 Mac/Win 布局，保留 VIA、自定义键位、旋钮和原厂 Custom 键功能。

**当前已验收固件：1.1.1；基于 QMK 0.34.6。** QMK 核心和硬件驱动零修改，使用官方 **External Userspace** 管理约 236 行自定义 keymap 文件，不需要维护 QMK fork。

## 行为

| 检测结果 | 默认布局 |
| --- | --- |
| macOS / iOS | Mac：基础层 0，Fn 层 1 |
| Windows / Linux | Win：基础层 2，Fn 层 3 |
| 未识别 | 保持当前层 |

实体 Mac/Win 开关仍可在自动识别完成后手动覆盖。OS 检测是 USB 枚举特征推测，不是身份查询；KVM 兼容性依赖具体连接方式。

## 快速开始

目标仅适用于 **Keychron V1 ANSI 旋钮版**，VID/PID `3434:0311`，QMK target `keychron/v1/ansi_encoder`。不要刷到 V1 Max、V1 8K、ISO 或无旋钮版本。

准备好 ARM GCC、make、dfu-util、hidapi、Python 和 Node 后：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
npm ci --ignore-scripts --no-audit --no-fund
.venv/bin/python scripts/setup_qmk.py
bash scripts/build.sh
bash scripts/test.sh
```

- 源码：`keyboards/keychron/v1/ansi_encoder/keymaps/auto_os/`
- QMK 锁定：`data/upstream.lock.json`（tag 与完整 SHA）
- 当前 VIA 定义：`via/keychron-v1-auto-os-v1.1.1.json`
- 只读设备诊断：`.venv/bin/python scripts/read_status.py`
- 本地包：`source scripts/env.sh && python scripts/package_release.py`

**构建/CI 不会刷机。** 原始闪存、VIA 私人备份、临时文件和上游 checkout 不进入 Git。

## 文档导航

- [需求与验收](docs/requirements.md)：最终布局规则、非目标、测试边界。
- [架构与改动边界](docs/architecture.md)：为什么用 userspace、改了哪些文件、数据来源。
- [构建与发布](docs/development.md)：本机/CI 构建、版本与 artifact 管理。
- [更新 QMK](docs/updating-qmk.md)：获取上游版本、处理兼容性、验收与回退。
- [刷机与恢复](docs/flashing.md)：手动 DFU、备份、读回校验。
- [测试记录](docs/testing.md)：已证实结果与尚未覆盖项目。
- [GitHub 管理](docs/github.md)：公开仓库、上传检查、分支/tag/Release。
- [VIA 使用](via/README.md) / [改动历史](CHANGELOG.md)。

## 仓库与本地资料

```text
keyboards/   我们的固件源代码（唯一编辑入口）
data/        上游锁定、公开厂商定义、经评审的键位基线
scripts/     构建、校验、备份/诊断工具
tests/       行为/兼容性测试与脱敏历史布局 fixture
via/         配套定义与说明
docs/        需求、设计、升级、验收文档
```

`qmk_firmware/`、`backups/`、`work/`、`qmk-v1-research/`、`.venv/`、`node_modules/`、`dist/` 仅本地保留并忽略。原来的研究资料及硬件回退备份没有删除。

代码采用 GPL-2.0-or-later，保留 QMK/Keychron 归属；第三方资料来源和许可注意事项见架构文档。
