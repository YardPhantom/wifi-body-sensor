"""
Win32 Native Wifi and ICMP Micro-Probing Interface
Interacts directly with Windows wlanapi.dll and iphlpapi.dll using ctypes.
"""

import ctypes
from ctypes import wintypes
import time
import subprocess
import re

# Win32 WLAN API setup
wlan = ctypes.windll.wlanapi
iphlpapi = ctypes.windll.iphlpapi
kernel32 = ctypes.windll.kernel32

wlan.WlanFreeMemory.argtypes = [ctypes.c_void_p]
wlan.WlanFreeMemory.restype = None

wlan.WlanOpenHandle.argtypes = [wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.HANDLE)]
wlan.WlanOpenHandle.restype = wintypes.DWORD

wlan.WlanCloseHandle.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
wlan.WlanCloseHandle.restype = wintypes.DWORD

wlan.WlanEnumInterfaces.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
wlan.WlanEnumInterfaces.restype = wintypes.DWORD

wlan.WlanGetNetworkBssList.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    wintypes.BOOL,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p)
]
wlan.WlanGetNetworkBssList.restype = wintypes.DWORD

wlan.WlanQueryInterface.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.c_void_p,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(wintypes.DWORD)
]
wlan.WlanQueryInterface.restype = wintypes.DWORD

# ICMP API Setup
iphlpapi.IcmpCreateFile.restype = wintypes.HANDLE
iphlpapi.IcmpCloseHandle.argtypes = [wintypes.HANDLE]
iphlpapi.IcmpCloseHandle.restype = wintypes.BOOL

iphlpapi.IcmpSendEcho.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    ctypes.c_char_p,
    wintypes.WORD,
    ctypes.c_void_p,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD
]
iphlpapi.IcmpSendEcho.restype = wintypes.DWORD

# Structures
class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', wintypes.BYTE * 8)
    ]

class WLAN_INTERFACE_INFO(ctypes.Structure):
    _fields_ = [
        ('InterfaceGuid', GUID),
        ('strInterfaceDescription', wintypes.WCHAR * 256),
        ('isState', wintypes.DWORD)
    ]

class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
    _fields_ = [
        ('dwNumberOfItems', wintypes.DWORD),
        ('dwIndex', wintypes.DWORD),
        ('InterfaceInfo', WLAN_INTERFACE_INFO * 1)
    ]

class DOT11_SSID(ctypes.Structure):
    _fields_ = [
        ('uSSIDLength', wintypes.ULONG),
        ('ucSSID', ctypes.c_char * 32)
    ]

class WLAN_RATE_SET(ctypes.Structure):
    _fields_ = [
        ('uRateSetLength', wintypes.ULONG),
        ('usRateSet', wintypes.USHORT * 126)
    ]

class WLAN_BSS_ENTRY(ctypes.Structure):
    _fields_ = [
        ('dot11Ssid', DOT11_SSID),
        ('uPhyId', wintypes.ULONG),
        ('dot11Bssid', ctypes.c_ubyte * 6),
        ('dot11BssType', wintypes.ULONG),
        ('dot11BssPhyType', wintypes.ULONG),
        ('lRssi', ctypes.c_long),
        ('uLinkQuality', wintypes.ULONG),
        ('bInRegDomain', wintypes.BOOLEAN),
        ('usBeaconPeriod', wintypes.USHORT),
        ('ullTimestamp', ctypes.c_ulonglong),
        ('ullHostTimestamp', ctypes.c_ulonglong),
        ('usCapabilityInformation', wintypes.USHORT),
        ('ulChCenterFrequency', wintypes.ULONG),
        ('wlanRateSet', WLAN_RATE_SET),
        ('ulIeOffset', wintypes.ULONG),
        ('ulIeSize', wintypes.ULONG)
    ]

class WLAN_ASSOCIATION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('dot11Ssid', DOT11_SSID),
        ('dot11BssType', wintypes.ULONG),
        ('dot11Bssid', ctypes.c_ubyte * 6),
        ('dot11PhyType', wintypes.ULONG),
        ('uDot11PhyIndex', wintypes.ULONG),
        ('wlanSignalQuality', wintypes.ULONG),
        ('ulRxRate', wintypes.ULONG),
        ('ulTxRate', wintypes.ULONG)
    ]

class WLAN_SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('bSecurityEnabled', wintypes.BOOL),
        ('bOneXEnabled', wintypes.BOOL),
        ('dot11AuthAlgorithm', wintypes.ULONG),
        ('dot11CipherAlgorithm', wintypes.ULONG)
    ]

class WLAN_CONNECTION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('isState', wintypes.DWORD),
        ('wlanConnectionMode', wintypes.DWORD),
        ('strProfileName', wintypes.WCHAR * 256),
        ('wlanAssociationAttributes', WLAN_ASSOCIATION_ATTRIBUTES),
        ('wlanSecurityAttributes', WLAN_SECURITY_ATTRIBUTES)
    ]

class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('Ttl', ctypes.c_ubyte),
        ('Tos', ctypes.c_ubyte),
        ('Flags', ctypes.c_ubyte),
        ('OptionsSize', ctypes.c_ubyte),
        ('OptionsData', ctypes.c_void_p)
    ]

class ICMP_ECHO_REPLY(ctypes.Structure):
    _fields_ = [
        ('Address', wintypes.DWORD),
        ('Status', wintypes.ULONG),
        ('RoundTripTime', wintypes.ULONG),
        ('DataSize', wintypes.USHORT),
        ('Reserved', wintypes.USHORT),
        ('Data', ctypes.c_void_p),
        ('Options', IP_OPTION_INFORMATION)
    ]


class Win32WifiMonitor:
    def __init__(self):
        self.wlan_handle = None
        self.interface_guid = None
        self.interface_desc = ""
        self.gateway_ip = self._detect_gateway_ip()
        self.gateway_int = self._ip_to_int(self.gateway_ip) if self.gateway_ip else 0
        
        # ICMP handle
        self.icmp_handle = iphlpapi.IcmpCreateFile()
        self.send_payload = b'WIFI_THROUGH_WALL_RADAR'
        self.reply_size = ctypes.sizeof(ICMP_ECHO_REPLY) + len(self.send_payload) + 64
        self.reply_buffer = ctypes.create_string_buffer(self.reply_size)

        # High resolution timer
        self.qpc_freq = ctypes.c_int64()
        kernel32.QueryPerformanceFrequency(ctypes.byref(self.qpc_freq))

        self._init_wlan()

    def _ip_to_int(self, ip_str: str) -> int:
        try:
            parts = [int(p) for p in ip_str.split('.')]
            return sum([p << (8 * i) for i, p in enumerate(parts)])
        except Exception:
            return 0

    def _detect_gateway_ip(self) -> str:
        """Find the Wi-Fi default gateway IPv4 address rapidly."""
        try:
            out = subprocess.check_output('netsh interface ipv4 show addresses "Wi-Fi"', shell=True, text=True)
            for line in out.splitlines():
                if "Default Gateway" in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
        except Exception:
            pass

        # Fallback to ipconfig parse
        try:
            out = subprocess.check_output("ipconfig", text=True)
            in_wifi = False
            for line in out.splitlines():
                if "Wireless LAN adapter Wi-Fi:" in line or "adapter Wi-Fi" in line:
                    in_wifi = True
                elif in_wifi and "adapter" in line:
                    in_wifi = False
                elif in_wifi and "Default Gateway" in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
        except Exception:
            pass

        return "192.168.1.254"

    def _init_wlan(self):
        h = wintypes.HANDLE()
        neg = wintypes.DWORD()
        res = wlan.WlanOpenHandle(2, None, ctypes.byref(neg), ctypes.byref(h))
        if res != 0:
            raise RuntimeError(f"WlanOpenHandle failed with code {res}")
        self.wlan_handle = h

        p_list = ctypes.c_void_p()
        res = wlan.WlanEnumInterfaces(self.wlan_handle, None, ctypes.byref(p_list))
        if res != 0 or not p_list:
            raise RuntimeError(f"WlanEnumInterfaces failed with code {res}")

        info_list = ctypes.cast(p_list, ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)).contents
        if info_list.dwNumberOfItems == 0:
            wlan.WlanFreeMemory(p_list)
            raise RuntimeError("No Wi-Fi interface found")

        self.interface_guid = GUID()
        ctypes.memmove(
            ctypes.byref(self.interface_guid),
            ctypes.byref(info_list.InterfaceInfo[0].InterfaceGuid),
            ctypes.sizeof(GUID)
        )
        self.interface_desc = info_list.InterfaceInfo[0].strInterfaceDescription
        wlan.WlanFreeMemory(p_list)

    def probe_icmp(self) -> float:
        """
        Sends a single ICMP echo to the gateway with microsecond precision.
        Returns round trip time in milliseconds. If timed out or failed, returns -1.0.
        """
        if not self.gateway_int or not self.icmp_handle:
            return -1.0

        t0 = ctypes.c_int64()
        t1 = ctypes.c_int64()
        kernel32.QueryPerformanceCounter(ctypes.byref(t0))

        res = iphlpapi.IcmpSendEcho(
            self.icmp_handle,
            self.gateway_int,
            self.send_payload,
            len(self.send_payload),
            None,
            self.reply_buffer,
            self.reply_size,
            150  # 150 ms timeout
        )
        kernel32.QueryPerformanceCounter(ctypes.byref(t1))

        if res > 0:
            elapsed_us = (t1.value - t0.value) * 1_000_000 / self.qpc_freq.value
            return elapsed_us / 1000.0  # in ms
        return -1.0

    def query_metrics(self) -> dict:
        """
        Captures instantaneous physical layer parameters:
        - RSSI (dBm)
        - Link Quality (%)
        - Frequency (MHz) & Channel
        - SSID & BSSID
        - Tx Rate / Rx Rate (Mbps)
        - ICMP RTT Jitter (ms)
        """
        data = {
            "timestamp": time.time(),
            "connected": False,
            "interface": self.interface_desc,
            "ssid": "",
            "bssid": "",
            "rssi": -100,
            "link_quality": 0,
            "frequency_mhz": 0,
            "channel": 0,
            "tx_rate_mbps": 0.0,
            "rx_rate_mbps": 0.0,
            "rtt_ms": -1.0,
            "gateway_ip": self.gateway_ip
        }

        target_bssid_bytes = None

        # 1. Query Current Connection Attributes first to get exact connected BSSID & speeds
        data_size = wintypes.DWORD()
        p_conn = ctypes.c_void_p()
        opcode_val = wintypes.DWORD()
        res_conn = wlan.WlanQueryInterface(
            self.wlan_handle,
            ctypes.byref(self.interface_guid),
            7,  # wlan_intf_opcode_current_connection
            None,
            ctypes.byref(data_size),
            ctypes.byref(p_conn),
            ctypes.byref(opcode_val)
        )

        if res_conn == 0 and p_conn:
            conn = ctypes.cast(p_conn, ctypes.POINTER(WLAN_CONNECTION_ATTRIBUTES)).contents
            assoc = conn.wlanAssociationAttributes
            data["rx_rate_mbps"] = round(assoc.ulRxRate / 1000.0, 1)
            data["tx_rate_mbps"] = round(assoc.ulTxRate / 1000.0, 1)
            data["link_quality"] = int(assoc.wlanSignalQuality)
            data["connected"] = True
            
            # Extract SSID
            ssid_len = assoc.dot11Ssid.uSSIDLength
            if ssid_len > 0:
                data["ssid"] = assoc.dot11Ssid.ucSSID[:ssid_len].decode('utf-8', errors='ignore')
            elif conn.strProfileName:
                data["ssid"] = conn.strProfileName

            target_bssid_bytes = bytes(assoc.dot11Bssid)
            data["bssid"] = ':'.join(f'{b:02x}' for b in target_bssid_bytes)
            wlan.WlanFreeMemory(p_conn)

        # 2. Query BSS List for RSSI and Frequency matching target BSSID
        p_bss = ctypes.c_void_p()
        res_bss = wlan.WlanGetNetworkBssList(
            self.wlan_handle,
            ctypes.byref(self.interface_guid),
            None,
            3,  # dot11_BSS_type_any
            False,
            None,
            ctypes.byref(p_bss)
        )

        if res_bss == 0 and p_bss:
            # Dynamically read total entries
            dw_items = ctypes.cast(p_bss, ctypes.POINTER(wintypes.DWORD * 2)).contents[1]
            if dw_items > 0:
                class WLAN_BSS_LIST_DYN(ctypes.Structure):
                    _fields_ = [
                        ('dwTotalSize', wintypes.DWORD),
                        ('dwNumberOfItems', wintypes.DWORD),
                        ('BSSList', WLAN_BSS_ENTRY * dw_items)
                    ]
                raw_bss = ctypes.cast(p_bss, ctypes.POINTER(WLAN_BSS_LIST_DYN)).contents
                matched_entry = None

                if target_bssid_bytes:
                    for i in range(dw_items):
                        entry = raw_bss.BSSList[i]
                        if bytes(entry.dot11Bssid) == target_bssid_bytes:
                            matched_entry = entry
                            break

                # Fallback to first entry if not matched
                if not matched_entry and dw_items > 0:
                    matched_entry = raw_bss.BSSList[0]

                if matched_entry:
                    data["rssi"] = int(matched_entry.lRssi)
                    if not data["link_quality"]:
                        data["link_quality"] = int(matched_entry.uLinkQuality)
                    data["frequency_mhz"] = int(matched_entry.ulChCenterFrequency / 1000)
                    
                    # Channel calculation
                    f = data["frequency_mhz"]
                    if 2412 <= f <= 2484:
                        data["channel"] = (f - 2407) // 5 if f != 2484 else 14
                    elif 5170 <= f <= 5835:
                        data["channel"] = (f - 5000) // 5
                    elif f > 5900:
                        data["channel"] = (f - 5950) // 5

            wlan.WlanFreeMemory(p_bss)

        # 3. Probe gateway latency
        data["rtt_ms"] = round(self.probe_icmp(), 3)

        return data

    def close(self):
        if self.icmp_handle:
            try:
                iphlpapi.IcmpCloseHandle(self.icmp_handle)
            except Exception:
                pass
            self.icmp_handle = None

        if self.wlan_handle:
            try:
                wlan.WlanCloseHandle(self.wlan_handle, None)
            except Exception:
                pass
            self.wlan_handle = None
