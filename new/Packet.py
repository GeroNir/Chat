class Packet:
    def __init__(self, data, id):
        self.data = data
        self.length = len(data)
        self.id = id
        self.checksum = self.calculate_checksum()

    def calculate_checksum(self):
        checksum = 0
        for byte in self.data:
            checksum += byte
        checksum = checksum % 256
        return checksum

    def get_data(self):
        return self.data

    def is_valid(self):
        return self.checksum == self.calculate_checksum()

    def __str__(self):
        return "Packet(length={}, checksum={}, data={}, id={})".format(self.length, self.checksum, self.data, self.id)