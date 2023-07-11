class Peer:
    def __init__(self, name, public_key, pre_shared_key, endpoint, allowed_ips, latest_handshake, transfer, active):
        self.name = name
        self.public_key = public_key
        self.pre_shared_key = pre_shared_key
        self.endpoint = endpoint
        self.allowed_ips = allowed_ips
        self.latest_handshake = latest_handshake
        self.transfer = transfer
        self.active = active

    def __str__(self):
        return f"{self.name}\t{self.public_key}\t{self.pre_shared_key}\t{self.endpoint}\t{self.allowed_ips}\t" \
               f"{self.latest_handshake}\t{self.transfer}\t{self.active}"

    def show_string(self):
        string = ""
        string += "name: " + self.name + "\n"
        string += "endpoint: " + self.endpoint + "\n"
        string += "allowed_ips: " + self.allowed_ips + "\n"
        string += "latest_handshake: " + self.latest_handshake + "\n"
        string += "transfer: " + str(self.transfer) + "\n"
        string += "active: " + str(self.active) + "\n"
        return string
