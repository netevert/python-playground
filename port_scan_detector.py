"""
Simple port scanning detector: given a PCAP file this script will
attempt to identify IP addresses that may be executing TCP SYN
port scans. IP addresses that send a higher ratio of SYN packets
compared to SYN-ACK packets received are flagged as suspect. The
ratio can be specified through command line options  

Test with this file:
https://github.com/sangh42/Port-Scan-Detector/blob/master/packets.pcap.xz
"""

import argparse
import dpkt, socket

class TcpPacket:
    def __init__(self, tcp):

        self.packet_flags = list()

        if tcp.flags & dpkt.tcp.TH_FIN != 0:
            self.packet_flags.append('FIN')
        if tcp.flags & dpkt.tcp.TH_SYN != 0:
            self.packet_flags.append('SYN')
        if tcp.flags & dpkt.tcp.TH_RST  != 0:
            self.packet_flags.append('RST')
        if tcp.flags & dpkt.tcp.TH_PUSH != 0:
            self.packet_flags.append('PSH')
        if tcp.flags & dpkt.tcp.TH_ACK  != 0:
            self.packet_flags.append('ACK')
        if tcp.flags & dpkt.tcp.TH_URG  != 0:
            self.packet_flags.append('URG')
        if tcp.flags & dpkt.tcp.TH_ECE  != 0:
            self.packet_flags.append('ECE')
        if tcp.flags & dpkt.tcp.TH_CWR  != 0:
            self.packet_flags.append('CWR')

    def return_flags(self):
        return self.packet_flags

class PacketAnalyzer:
    def __init__(self, pcap_file, ratio):
        
        try:
            self.pcap = dpkt.pcap.Reader(open(pcap_file, 'rb'))
        except (IOError, KeyError):
            print("Cannot open PCAP file")

        self.ratio = float(ratio)
        self.suspect_ips = dict()
        self.packet_count = 0

    def compare_ips(self, ip1, ip2):
        """
        Return negative if ip1 < ip2, 0 if they are equal, positive if ip1 > ip2.
        """
        return sum(map(int, ip1.split('.'))) - sum(map(int, ip2.split('.')))

    def analyze(self):
        for _, buf in self.pcap:
            self.packet_count += 1

            # ignore malformed packets
            try:
                eth = dpkt.ethernet.Ethernet(buf)
            except (dpkt.dpkt.UnpackError, IndexError):
                continue

            # Packet must include IP protocol to get TCP
            ip = eth.data
            if not ip:
                continue

            # Skip packets that are not TCP
            tcp = ip.data
            if type(tcp) != dpkt.tcp.TCP:
                continue

            # Grab all flags in this TCP packet
            tcp_flags = TcpPacket(tcp).return_flags()

            source_ip = socket.inet_ntoa(ip.src)
            destination_ip = socket.inet_ntoa(ip.dst)

            # Fingerprint possible suspects.
            if {'SYN'} == set(tcp_flags):          # A 'SYN' request.
                if source_ip not in self.suspect_ips:
                    self.suspect_ips[source_ip] = {'SYN': 0, 'SYN-ACK': 0}
                self.suspect_ips[source_ip]['SYN'] += 1
            elif {'SYN', 'ACK'} == set(tcp_flags): # A 'SYN-ACK' reply.
                if destination_ip not in self.suspect_ips: 
                    self.suspect_ips[destination_ip] = {'SYN': 0, 'SYN-ACK': 0}
                self.suspect_ips[destination_ip]['SYN-ACK'] += 1

            # Prune unlikely suspects based on ratio of SYNs to SYN-ACKs.
            for ip in list(self.suspect_ips):
                if self.suspect_ips[ip]['SYN'] < (self.suspect_ips[ip]['SYN-ACK'] * self.ratio):
                    del self.suspect_ips[ip]

        self.print_results()
    
    def print_results(self):
        print("Analyzed {} packets...".format(self.packet_count))

        if not self.suspect_ips:
            print("No suspicious packets found")

        for suspect_ip in self.suspect_ips.keys():
            print("{:15} had {} SYNs and {} SYN-ACKs".format(suspect_ip, 
                                                            self.suspect_ips[suspect_ip]["SYN"],
                                                            self.suspect_ips[suspect_ip]["SYN-ACK"]))

def main():
    # Set-up command line options
    parser = argparse.ArgumentParser(description="Simple port scan detection script")
    parser.add_argument("-f", "--file", help="Target PCAP file", required=True)
    parser.add_argument("-r", "--ratio", help="Ratio of SYN packets sent vs SYN-ACK received", type=int, default=3, required=False)
    args = parser.parse_args()

    print("Running analysis on PCAP file: {}".format(args.file))
    print("Selected ratio: {}".format(args.ratio))
    PacketAnalyzer(args.file, args.ratio).analyze()


if __name__ == "__main__":
    main()
