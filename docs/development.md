# 构建、测试和发布

## 首次准备

macOS 已安装的依赖：Homebrew `make`、`dfu-util`、`hidapi`、`osx-cross/arm/arm-none-eabi-gcc@8` 及 binutils。工具链版本为 GCC 8.5.0 / binutils 2.41；不需要修改全局 shell 配置。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
npm ci --ignore-scripts --no-audit --no-fund
.venv/bin/python scripts/setup_qmk.py
bash scripts/build.sh
bash scripts/test.sh
```

运行环境推荐 Python 3.14、Node 22 或更新版本。依赖首次安装需要网络。`env.sh` 在当前进程设置 `QMK_HOME`、`QMK_USERSPACE` 和工具 PATH，不更改个人 QMK 全局配置。

`setup_qmk.py` 下载固定 QMK；已有 checkout 不符时会停止，而不是 reset/覆盖。固件生成到 `qmk_firmware/` 和 userspace 根目录，二者都不会提交 bin。

## 日常修改

1. 功能或修复建分支，例如 `fix/linux-detection`。
2. 修改 `keyboards/.../auto_os/`。不在 QMK 依赖目录编辑。
3. 更改切层策略则改 C 测试；改键位则审查并更新 `data/expected-keymap.json`。
4. 构建会生成 VIA JSON 和灯效断言。将合理的生成文件变化一起提交。
5. `bash scripts/test.sh`；再看 `git diff`，不能只凭编译成功。
6. 硬件测试通过后记录在 `docs/testing.md`，再决定发布。

GitHub Actions 对 push/PR 自动编译与校验，输出 bin、VIA JSON 和构建清单；**绝不自动刷机**。工作流为只读权限，不使用个人凭据；首次云端运行已通过，详见测试记录。Linux CI 使用系统 ARM 工具链，可能与本机 GCC 8 生成不同字节，云端成功不等于硬件验收。

## 发布

软件版本在 `VERSION` 和 `config.h` 的 `VIA_FIRMWARE_VERSION` 同步修改，例如 `1.2.0` → `0x00010200`。文档与测试结果同步更新。

```sh
source scripts/env.sh
python scripts/package_release.py
```

输出 `dist/auto-os-版本号/`，包含 bin、VIA JSON、manifest（源提交、QMK SHA、编译器、校验值、dirty 标记）。默认标记“本次构建未硬件测试”；必须有测试记录才能提升为已验收版本。

建议使用 `firmware-v1.1.2` 这样的 Git tag；发布前确保工作区干净，tag 指向对应源码。GitHub Release 可附匹配文件，不把大量历史 bin 放进 Git 历史。

已刷入的 1.1.1 二进制保留在本地备份，SHA256 为：
`4009c884b32e8e048d9c5fd8e12262847bdf95a48b48bd09ca49f662f3f580bb`。
这次仓库整理没有重新刷机；userspace 迁移构建与该文件字节一致。
