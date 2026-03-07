"""
CyberSentinel - Packet Sniffer Module
=======================================
Captures real-time network packets using scapy and extracts
key information: source IP, destination IP, protocol, and port.

Uses a callback-based architecture so captured packet data
can be forwarded to detection engines for analysis.

NOTE: Packet sniffing requires administrator/root privileges.
"""

import time
import threading
from typing import Callable

from scapy.all import sniff, IP, TCP, UDP, ICMP, conf

from app.utils.logger import get_logger


# Initialize module logger
logger = get_logger("sniffer")

# Protocol number to name mapping
PROTOCOL_MAP = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}


class PacketSniffer:
    """
    Real-time network packet sniffer using scapy.

    Captures packets from a network interface, extracts metadata
    (source IP, dest IP, protocol, port), and dispatches parsed
    packet data to registered handler callbacks.

    Attributes:
        interface: Network interface to sniff on (None = default).
        bpf_filter: Berkeley Packet Filter string for scapy.
        max_packets: Maximum number of packets to capture (0 = unlimited).
        packet_count: Total number of packets captured so far.
    """

    def __init__(
        self,
        interface: str | None = None,
        bpf_filter: str | None = None,
        max_packets: int = 0,
    ):
        """
        Initialize the packet sniffer.

        Args:
            interface: Network interface name (e.g., 'eth0', 'Wi-Fi').
                       None = use scapy's default interface.
            bpf_filter: BPF filter expression (e.g., 'tcp', 'port 80').
            max_packets: Stop after capturing this many packets (0 = unlimited).
        """
        self.interface = interface
        self.bpf_filter = bpf_filter
        self.max_packets = max_packets

        # Packet counter (thread-safe via GIL for simple increments)
        self.packet_count: int = 0

        # List of callback functions to receive parsed packet data
        self._handlers: list[Callable[[dict], None]] = []

        # Control flag for stopping the sniffer
        self._running = threading.Event()

        # Suppress scapy's verbose output
        conf.verb = 0

        logger.info(
            "PacketSniffer initialized | interface=%s | filter=%s | max_packets=%s",
            self.interface or "default",
            self.bpf_filter or "none",
            self.max_packets or "unlimited",
        )

    def register_handler(self, handler: Callable[[dict], None]) -> None:
        """
        Register a callback function to process captured packets.

        The handler receives a dictionary with parsed packet metadata:
            {
                "timestamp": float,
                "src_ip": str,
                "dst_ip": str,
                "protocol": str,
                "src_port": int | None,
                "dst_port": int | None,
                "size": int,
            }

        Args:
            handler: Callable that accepts a packet data dictionary.
        """
        self._handlers.append(handler)
        logger.debug("Registered packet handler: %s", handler.__name__)

    def _process_packet(self, packet) -> None:
        """
        Internal callback for scapy's sniff function.

        Extracts IP-layer information from each captured packet
        and dispatches it to all registered handlers.

        Args:
            packet: Raw scapy packet object.
        """
        # Only process packets with an IP layer
        if not packet.haslayer(IP):
            return

        # Increment packet counter
        self.packet_count += 1

        # Extract IP layer information
        ip_layer = packet[IP]
        protocol_num = ip_layer.proto
        protocol_name = PROTOCOL_MAP.get(protocol_num, f"OTHER({protocol_num})")

        # Build the parsed packet data dictionary
        packet_data = {
            "timestamp": time.time(),
            "src_ip": ip_layer.src,
            "dst_ip": ip_layer.dst,
            "protocol": protocol_name,
            "src_port": None,
            "dst_port": None,
            "size": len(packet),
        }

        # Extract port information for TCP/UDP
        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            packet_data["src_port"] = tcp_layer.sport
            packet_data["dst_port"] = tcp_layer.dport
        elif packet.haslayer(UDP):
            udp_layer = packet[UDP]
            packet_data["src_port"] = udp_layer.sport
            packet_data["dst_port"] = udp_layer.dport

        # Log every 100th packet to avoid overwhelming the console
        if self.packet_count % 100 == 0:
            logger.info(
                "Packets captured: %d | Latest: %s → %s [%s]",
                self.packet_count,
                packet_data["src_ip"],
                packet_data["dst_ip"],
                protocol_name,
            )

        # Dispatch to all registered handlers
        for handler in self._handlers:
            try:
                handler(packet_data)
            except Exception as e:
                logger.error(
                    "Error in packet handler '%s': %s",
                    handler.__name__,
                    str(e),
                )

    def _stop_filter(self, _packet) -> bool:
        """
        Stop filter callback for scapy sniff.
        Returns True to stop sniffing when the running flag is cleared.
        """
        return not self._running.is_set()

    def start(self) -> None:
        """
        Start capturing network packets.

        This method blocks until stop() is called or max_packets is reached.
        Must be run with administrator/root privileges.
        """
        self._running.set()
        logger.info("🔍 Packet sniffer STARTED — listening for traffic...")

        try:
            sniff_kwargs = {
                "prn": self._process_packet,
                "store": False,  # Don't store packets in memory
                "stop_filter": self._stop_filter,
            }

            # Optional parameters
            if self.interface:
                sniff_kwargs["iface"] = self.interface
            if self.bpf_filter:
                sniff_kwargs["filter"] = self.bpf_filter
            if self.max_packets > 0:
                sniff_kwargs["count"] = self.max_packets

            # Start scapy's packet capture
            sniff(**sniff_kwargs)

        except PermissionError:
            logger.critical(
                "❌ Permission denied! Packet sniffing requires admin/root privileges. "
                "Please run CyberSentinel as Administrator (Windows) or with sudo (Linux/Mac)."
            )
            raise
        except Exception as e:
            logger.error("Sniffer error: %s", str(e))
            raise
        finally:
            self._running.clear()
            logger.info(
                "🛑 Packet sniffer STOPPED — Total packets captured: %d",
                self.packet_count,
            )

    def stop(self) -> None:
        """
        Signal the sniffer to stop capturing packets.
        The sniffer will stop after processing the current packet.
        """
        logger.info("Stopping packet sniffer...")
        self._running.clear()

    @property
    def is_running(self) -> bool:
        """Check if the sniffer is currently running."""
        return self._running.is_set()
