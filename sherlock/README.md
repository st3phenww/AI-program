# Sherlock 云端试用与本地迁移包

准备日期：2026-11-08（悉尼）。上游：[sherlock-project/sherlock](https://github.com/sherlock-project/sherlock)。固定版本：0.16.2。验证环境：Linux + Python 3.12.14。

## 它有什么用

输入用户名后，Sherlock 按各网站的公开网址和响应规则检查是否存在同名账号。适合找回自己的旧账号、查看网名是否被使用、学习 Python 网络请求与开源情报（OSINT）工具的工作原理。

它不使用大语言模型，不需要 OpenAI API Key，也不消耗模型 API 额度。它不需要 GPU。主要依赖网络连通性；查到同名账号不代表确认了账号主人。它不会破解账号，也不保证查全所有平台。

## 当前已完成什么

- 当前 ChatGPT 云端会话环境已安装原版 Sherlock 0.16.2，独立虚拟环境中的依赖已检查。
- 查询仍由原版 Sherlock 执行，run.py 只负责参数、文件保存和中文 HTML 展示。
- 这是按需运行的云端命令行环境，没有独立的永久公网网址，也不保证会话休眠后的进程或安装目录继续存在。
- 安装包保留了启动器、版本锁定文件和验证记录，方便在新的云主机或本地电脑重建。
- 本次没有连接或修改你的本地电脑；Windows、Mac 启动文件尚未在相应系统上实机验证。

## 在当前云端使用

在聊天中给出要查的用户名，以及要查的平台；例如“用 Sherlock 查这个用户名，只看 GitHub”。助手可在当前环境运行并返回结果。一次查询通常会向多个第三方网站发送用户名。

命令行使用：

```bash
.venv/bin/python run.py example_name --site GitHub
```

省略 `--site` 时按原版默认规则查询。可重复指定 `--site`。默认不启用成人站点。单站超时默认 15 秒，整体最多运行 10 分钟。

每次结果会放入独立的 `results/日期-随机标识/`，包含：

- `report.html`：中文卡片式结果，可在浏览器打开。
- `用户名.csv`：原始检测状态、HTTP 状态码等。
- `用户名.txt`：检测到的链接。
- `run.log` / `run.json`：日志和本次参数。

`--frozen-sites` 使用发行版内置规则，适合复现测试；它会跳过上游最新排除列表，不建议作为日常默认值。发行版内有 481 条网站规则，这不等于每次都能查到 481 个网站，也不保证各站规则始终有效。

## 后续部署到 Windows

1. 从 [Python 官网](https://www.python.org/downloads/) 安装 Python 3.12，包含 Python Launcher。
2. 解压本包到一个普通目录。
3. 双击 `Start-Windows.cmd`。首次运行会安装独立依赖，然后提示输入用户名。
4. 运行结束后，到 `results` 最新目录打开 `report.html`。

若需要手动重建依赖，在该目录的终端执行：

```powershell
py -3.12 setup.py
.venv\Scripts\python.exe run.py example_name --site GitHub
```

## 后续部署到 Mac

先安装 Python 3.12。首次运行前在解压目录的终端执行：

```bash
python3.12 setup.py
chmod +x Start-Mac.command
./Start-Mac.command
```

之后可双击 `Start-Mac.command`。如果 Finder 没有保留执行权限，可继续用终端运行。此工具不依赖 GPU，普通 Windows / Mac 电脑即可运行。

## 独立云主机部署

本包可在装有 Python 3.12 的 Linux 云主机上按同样方式安装：

```bash
python3.12 setup.py
.venv/bin/python run.py example_name --site GitHub
```

这里部署的是命令行程序。若需要手机打开网址就能使用，还需要可运行 Python 的长期托管账号/服务器，以及带身份验证的网页服务。当前没有开通收费主机、没有创建公网查询接口。

## 如何理解结果

| 原始状态 | 含义 |
| --- | --- |
| Claimed | 检测到同名公开账号，需打开主页人工核实 |
| Available | 本次未检测到；不代表账号不存在或名字一定可注册 |
| Unknown | 网络或其他查询错误，无法判断 |
| WAF | 网站反爬拦截，无法判断 |
| Illegal | 该用户名不符合目标网站格式 |

网站的验证码、封禁云机 IP、登录要求、规则变化都可能影响结果；云端与家用网络的结果可能不同。运行日志可能出现上游的推广信息，不需要为此访问或购买其他服务。

## 文件与版本

- `requirements.txt`：固定上游 Sherlock 版本。
- `requirements-lock.txt`：本次 Linux / Python 3.12 验证时的完整依赖版本。Windows / Mac 安装仍需联网下载对应系统的软件包。
- `run.py`、`setup.py`、两个启动器：此次新增的便捷工具。
- `VALIDATION.md`：实际验证结果和验证范围，不含个人查询。

上游 Sherlock 使用 MIT 许可，见 [上游许可证](https://github.com/sherlock-project/sherlock/blob/v0.16.2/LICENSE)。运行器不修改上游检测代码。请保留上游授权信息。
