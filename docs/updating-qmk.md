# 如何获取 QMK 更新

## 原则

**不跟随 master 自动升级，不定时刷固件。** 我们锁定已验证版本。需要上游功能或修复时再升级，先作为候选版本测试。

上游更新与我们业务改动分开提交：一个提交调整 QMK 锁定，一个提交处理不兼容问题；便于审查和回退。不要把 `git pull` 当升级策略。

## 步骤

1. 确认当前仓库干净、当前可用固件与 VIA 配置有备份；创建 `upgrade/qmk-X.Y.Z` 分支。
2. 在 QMK 官方仓库核对目标 release/tag 和完整 commit SHA，读两版间的 changelog，重点关注 OS detection、USB/ChibiOS、VIA/keycode 编号、RGB 和 V1 驱动。
3. 在**干净的** `qmk_firmware` checkout 中 fetch 该 tag、切到明确 SHA；不要改成自己的厂商 fork，也不要使用破坏性 reset。
4. 同步编辑 `data/upstream.lock.json` 的 tag/SHA，并执行 `scripts/setup_qmk.py` 更新必要子模块。
5. `bash scripts/build.sh && bash scripts/test.sh`；检查生成的 VIA JSON、灯效编号和所有断言。旧 `.build` 缓存不能作为新版本通过的证据，使用新的 checkout 或干净构建目录验证。
6. 如 QMK 改变键码编号，参考新版本定义重新评审布局基线；**不自动接受测试失败的数值**。
7. 硬件测试通过，记录 QMK/自定义固件版本及结果，再合并、打 tag、发布。

示例结构（`目标标签`、`完整SHA` 要用已核实值替换）：

```sh
git switch -c upgrade/qmk-目标标签
git -C qmk_firmware status --short
git -C qmk_firmware fetch --depth 1 origin tag 目标标签
git -C qmk_firmware switch --detach 完整SHA
# 审查并更新 data/upstream.lock.json
.venv/bin/python scripts/setup_qmk.py
bash scripts/build.sh
bash scripts/test.sh
```

QMK 目录有未提交改动时先处理；辅助脚本不会替你丢弃它们。

## 必测项目

- 直连 Mac / Linux / Windows；实体开关处于相反位置时自动选择仍正确。
- KVM 双向切换，尤其 Mac → Linux → Mac；保持键盘供电的切换行为。
- 未识别时维持当前层，手动拨动可纠正；休眠唤醒、关机主机切换。
- VIA 版本识别、四层/旋钮/宏读回、11 个 Custom 项、灯效菜单。
- 不同工具链生成的固件需重新硬件验证，不沿用旧二进制的验收结论。

## 回退

回退的是**配套的源码 tag、QMK SHA、固件 bin 和 VIA 定义**，不是只改一个文件。设备原始闪存和私人配置保存在本地 `backups/`，不进入 GitHub。手工从已知版本重建时先保留正在使用的固件。
