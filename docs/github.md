# GitHub 管理建议

建议新建独立 **私有** 仓库 `hyspace/keyboard-os-detect`，而不是 fork 整个 QMK。
私人配置备份不会被提交，但可编辑键位本身属于你的布局，公开前也应确认。

## 上传前

```sh
git status --short
git ls-files
git diff --cached --stat
```

应包含 keymap、测试、公开来源定义、布局基线、文档、锁文件、CI；不应包含
`backups/`、`work/`、`qmk_firmware/`、`.venv/`、node_modules、原始闪存或序列号。
`.gitignore` 不能清除已经进入历史的私密数据，因此必须在第一次提交前检查。

确认仓库名和可见性后，可用已经登录的 GitHub CLI：

```sh
gh repo create hyspace/keyboard-os-detect --private --source=. --remote=origin
git push -u origin main
```

同名仓库已存在时先检查内容，不强制推送、不覆盖已有历史。

## 建议工作流

- `main` 保持可构建、可回退；功能/上游升级用短期分支和 PR。
- CI 只编译、测试、提供构建 artifact；不自动创建“已硬件验证”release。
- 稳定版本用 `firmware-vX.Y.Z` tag + Release，附 bin、匹配 VIA JSON、manifest。
- 上游 QMK 始终由 `data/upstream.lock.json` 决定；GitHub 的“Sync fork”不是升级入口。
- 本地设备备份另作加密备份，不以 GitHub 代替它。

GitHub 凭据经本机 CLI 检查可用；当前文档中的创建命令只是操作步骤，是否已上传以实际远端状态为准。
