# 🔌 Network Watchdog —— 断网自动关机守护脚本

当网络完全中断时，自动安全关闭主机。  
**专为搭配 UPS（不间断电源）使用**，在断电后路由器/交换机先于服务器掉线的情况下，检测网络不可达并执行关机，保护数据与硬件。

---

## 🧠 设计思路

- **监控两个 IP**（一内一外），只有**两者同时 ping 不通**才认为网络真正中断。
- 采用**两阶段检测**：先发 1 个包快速试探，若都失败则补发 2 个包二次确认，避免偶发丢包导致误关机。
- 一旦确认网络完全中断，立即执行 `halt` 关机。
- 全程无屏幕输出，只写日志，适合部署为后台守护进程。

---

## 📦 适用场景

- 服务器、NAS 等连接 UPS，断电后 UPS 开始供电，但路由器/交换机可能未接入 UPS 先掉线。
- 当路由器掉线后，服务器虽然仍有 UPS 供电，但网络彻底不可达。
- 本脚本在确认网络完全中断后自动关机，避免服务器耗尽 UPS 电量后异常断电，保护文件系统与硬件。

---

## ⚙️ 功能

- 周期性 ping 内网 IP（如网关、光猫）与公网 IP（如 114.114.114.114）。
- 两次都失败 → 立即关机。
- 每次检测间隔 ≥ 2 秒，CPU 占用极低。
- 日志记录到 `/var/log/power_supply_check.log`，方便事后排查。

---

## 📋 要求

- **操作系统**：Linux（使用 systemd 管理为佳）
- **权限**：需能以 root 运行或具备免密码 `sudo halt` 权限
- **网络**：被监控的两个 IP 在正常状态下必须能稳定 ping 通

---

## 🚀 快速开始

### 1. 下载脚本

```bash
curl -O https://raw.githubusercontent.com/你的用户名/仓库名/main/network_watchdog.py
chmod +x network_watchdog.py

### 2. 修改监控目标（可选）
编辑脚本中的两个 IP：

python
IP_target_lan = '192.168.0.254'        # 内网 IP，例如路由器/光猫/网关
IP_target_wan = '114.114.114.114'      # 公网 IP，确保能 ping 通
### 3. 配置免密码关机（若非 root 运行）
bash
sudo visudo -f /etc/sudoers.d/network_watchdog
添加以下行（假设脚本由用户 pi 运行）：

text
pi ALL=(ALL) NOPASSWD: /sbin/halt
### 4. 注册为 systemd 服务（推荐）
创建服务文件 /etc/systemd/system/network-watchdog.service：

ini
[Unit]
Description=Network Watchdog - Auto shutdown on total network loss
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/network_watchdog.py
Restart=always
RestartSec=10
User=root
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
启动并启用：

bash
sudo systemctl daemon-reload
sudo systemctl enable --now network-watchdog.service
## 📄 日志
所有事件记录在 /var/log/power_supply_check.log：

INFO - 网络监控脚本启动

CRITICAL - 两次 ping 都失败，执行关机

正常运行时无任何日志写入，保持安静。
