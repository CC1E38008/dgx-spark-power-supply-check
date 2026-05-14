#!/usr/bin/env python3
import subprocess
import time
import logging

# ========== 监控目标配置 ==========
IP_target_lan = '192.168.0.254'          # 第一个监控 IP，推荐内网LAN或者光猫的IP或者网关
IP_target_wan = '114.114.114.114'        # 第二个监控 IP，推荐公网IP或者允许ping回包的公网DNS的IP
# =================================

# 配置日志
logging.basicConfig(
    filename='/var/log/power_supply_check.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ping(ip, count):
    """
    执行 ping 命令并返回是否成功。
    成功：至少收到一个包返回，返回 True。
    失败：所有包丢失、网络不可达、超时等，返回 False。
    """
    try:
        result = subprocess.run(
            ['ping', '-c', str(count), '-W', '1', ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # 退出状态码 0 表示至少有一个包返回
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Ping {ip} 失败: {e}")
        return False

def main():
    logging.info("网络监控脚本启动")
    while True:
        start_time = time.time()

        # 第一轮：快速探测 1 个包
        success_ip1 = ping(IP_target_lan, 1)
        success_ip2 = ping(IP_target_wan, 1)

        if not success_ip1 and not success_ip2:
            # 第一轮两个都失败后，第二轮用 2 个包降低偶发丢包影响
            success_ip1 = ping(IP_target_lan, 2)
            success_ip2 = ping(IP_target_wan, 2)

            if not success_ip1 and not success_ip2:
                logging.critical("两次 ping 都失败，执行关机")
                subprocess.run(['poweroff'])

        # 确保每轮检测间隔至少 2 秒
        elapsed = time.time() - start_time
        if elapsed < 2:
            time.sleep(2 - elapsed)

if __name__ == "__main__":
    main()
