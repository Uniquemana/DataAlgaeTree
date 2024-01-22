
class Device:
    def __init__(self, raw):
        r = list(raw)

        self.id = r[0]
        self.co2 = r[1]
        self.air_temperature = r[2]
        self.air_humidity = r[3]
        self.updated = r[7]

    def to_array(self):
        return {
            "deviceID": self.id,
            "CO2": round(self.co2),
            "air_temp": round(self.air_temperature),
            "air_humid": round(self.air_humidity),
            "timestamp": self.updated
        }
