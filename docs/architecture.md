# 改动边界与管理方式

## 结论：独立 External Userspace，不维护 QMK 大 fork

盘点时 QMK 跟踪文件改动为 **0**。新增 keymap 共 8 个文件、236 行，其中不少是键位表、配置和生成断言。真正的行为逻辑只有 OS 回调和 Keychron Custom 处理。

采用 QMK 官方 External Userspace：

```text
keyboards/keychron/v1/ansi_encoder/keymaps/auto_os/  自有固件源代码
qmk.json                                         QMK 官方构建入口
data/upstream.lock.json                           QMK tag + 精确 SHA
qmk_firmware/                                    忽略的原样依赖 checkout
scripts/ tests/ via/ docs/                        自有工具与文档
```

选择独立锁文件而不是 Git submodule 管理 QMK：本项目只有一个上游依赖，明确 SHA 的浅克隆更容易理解；QMK 内部子模块仍严格使用该提交锁定的版本。`check_upstream.py` 拒绝错版本、脏目录或不匹配的必要子模块。

与其他方案比较：
- **QMK fork**：若将来必须修改 USB 栈或硬件驱动才值得使用；现在合并噪声远大于收益。
- **补丁文件**：每次升级要手动应用，容易失去当前代码可见性，不如 userspace。
- **只保存 bin**：不能评审、重建或可靠升级，不适合长期管理。

官方说明：https://docs.qmk.fm/newbs_external_userspace

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `auto_os.c` | OS→默认层策略；VIA `0x02/0x80` 只读诊断，签名 `AOS1`。 |
| `auto_os.h` | Mac/Win 基础层和 Fn 层编号。 |
| `keychron_compat.c/.h` | `QK_KB_0..10` 对应官方 11 个 Custom 项和 500ms Siri 时序。 |
| `keymap.c` | 从用户原键位迁移的四层及旋钮；以后直接编辑此文件。 |
| `config.h` / `rules.mk` | OS 检测、VIA、旋钮和自定义源文件。 |
| `via_effects_check.h` | 自动生成：灯效编号/数量及 VIA 版本的编译期断言。 |

实体开关逻辑沿用 QMK 的 `v1.c`，没有复制到我们的目录。启动/变化时切层，不会持续覆盖自动检测。OS 枚举和重检测由上游 QMK 完成。

## 数据不是设备备份

- `data/expected-keymap.json` 是**经评审的布局基线**，用于比对固件里的数值。修改键位或升级导致键码变化时，明确评审后同步更新；不要自动让基线追随构建结果。
- `tests/fixtures/legacy-keymap.json` 只包含历史键位与矩阵/旋钮数据，不含宏、序列号或完整 EEPROM；用于测试旧编号迁移。
- `data/keychron-v1-official-via.json` 来自厂商公开定义，不来自私有设备。
- 原始闪存、VIA 配置、宏、硬件序列号与本地日志全部忽略，不参与构建。
- `generate_keymap.py` 仅供重看历史转换，输出到 `work/`，不会覆盖现在可编辑的 `keymap.c`。

## 来源与协议

- QMK：`0.34.6` / `d9f6dd215f2c4d295c6ad85b1f602125c2d81db1`。
- Keychron Custom 处理源自 GPL-2.0-or-later 代码：
  https://github.com/Keychron/qmk_firmware/blob/0456ffb38e67160e2c59a91ab00f424d3765f1f6/keyboards/keychron/common/keychron_common.c
- 官方 VIA 定义：
  https://cdn.shopify.com/s/files/1/0059/0630/1017/files/v1_us_knob_v1.7.json.zip?v=1681885405
- VIA app 核查提交：`935106a990af39bdd1ade881c02366eac486240d`。协议 13 的 `CUSTOM(n)` 基址为 `0x7E00`；原协议 11 是 `0x7F00`。
- 新固件不在运行时拦截旧 `0x7F00` 范围，因为与新 QMK 用户键码范围重叠。旧数据在迁移时转换，不直接恢复原始数值。
- VIA reader 1.14.4 校验器使用 GPL-3.0；仅为开发依赖，不链接进固件。其 schema 警告单独保留在本地日志。

我们的代码按 GPL-2.0-or-later 管理，保留上游归属。厂商 JSON 的转载许可未独立确认；先使用私有仓库，若要公开发布，审查第三方文件许可和固件源代码提供义务。
