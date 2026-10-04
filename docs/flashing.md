# 刷机、诊断与恢复

## 先确认硬件

只适用于 `3434:0311` / Keychron V1 ANSI 旋钮版。更新时正常直连电脑，不经过 KVM。
先读当前配置并保存，不默认原始布局仍与新固件的编译默认值一致：

```sh
.venv/bin/python scripts/backup_via.py backups/新的唯一备份名.json
.venv/bin/python scripts/read_status.py
```

VIA 备份脚本只读取配置，两次读取一致才保存；不采集按键输入。它不是 VIA GUI 导出，不能直接丢给 VIA 导入。宏可能含敏感内容，备份勿上传。

## 手动进入 DFU

用户选择继续手动操作，不新增软件 DFU 快捷键：拔线，按住 Esc 接回电脑，约 2 秒后松开。此时键盘不能输入，需备用输入方式。
Bootmagic 会使 EEPROM 配置失效，因此必须在这之前备份。

`QK_BOOT` 键码也能进入 DFU，但当前没有分配；电脑直接发送 VIA `0x0B` 的处理没有实现。不要把普通 `QK_REBOOT` 与进入 bootloader 混淆。

## 写入前后检查

1. `dfu-util -l` 查看实际设备，确认唯一目标 `0483:df11`、序列号/USB 路径、alternate 0 的内部闪存。
2. 使用**本次读取到的**设备选择器备份全部 256 KB 闪存，两次读取比对。不要在脚本中硬编码个人设备序列号。
3. 检查 bin SHA256、DFU suffix、正确型号；仅向 `0x08000000` 的内部闪存写本次固件。
4. 不使用 mass-erase、unprotect、force，不碰 OTP/Option Bytes。
5. 留在 DFU，上传读回并逐字节比较有效载荷；检查未写入的页没有变化，再发送 leave 重启。
6. 重启后确认 VIA 固件版本、四层/旋钮/宏读回；当前 OS/default layer 正确。记录失败/异常，不只看“Download done”。

命令模板（先替换已核实的序列号/路径，文件名必须唯一）：

```sh
dfu-util -d 0483:df11 -S 实际序列号 -p 实际路径 -a 0 -s 0x08000000:262144 -U backups/唯一的原闪存文件.bin
dfu-util -d 0483:df11 -S 实际序列号 -p 实际路径 -a 0 -s 0x08000000 -D 已校验的固件.bin
# 先读回核对，不立即跳过校验重启
dfu-util -d 0483:df11 -S 实际序列号 -p 实际路径 -a 0 -s 0x08000000:leave
```

## 测试与恢复

重启后先测直连，再测 KVM。如果 Linux 不切层，保持连接 Linux，在 Linux 上运行只读诊断；切回 Mac 会重新检测，不能据此推断上一个系统。

最初官方回退文件与实际设备固件前缀完全一致：V1 US Knob v1.7.1。我们另存了原始完整闪存和已用过的 1.1.0/1.1.1 文件。所有备份仍在本机 `backups/` 和 `work/previous-build/`。

恢复前重新核对硬件和文件，保留当前备份，再用相同的明确设备选择器操作。旧厂商固件与新 QMK 使用不同 Custom/RGB 编号，不能跨版本原样恢复 raw VIA keycodes。
