import paho.mqtt.client as mqtt
import time
import json

# Service Mode
# Pool Mode
# Spa Mode
# Filter Pump
# Pool Light
# Heater
# Spa Light
# Blower
# Cleaner 
# Waterfall

# Sensors:
# Pool Time Correct - Binary
# Outside Air Temp - Regular Sensor
# Pool Temp - Regular Sensor
# Spa Temp - RS


class MyLogger():
    def __init__(self):
        pass
    def log(self,log_text):
        print(log_text)

class AquaLogic():
    """Hayward/Goldline AquaLogic/ProLogic pool controller."""

    def __init__(self):
        self.air_temp = None
        self.pool_temp = None
        self.spa_temp = None
        self.salt_level = None
        self.topics =   {"pool_temperature_addr"    : "pool/pool_temperature",
                         "spa_temperature_addr"     : "pool/spa_temperature",
                         "outside_temperature_addr" : "pool/outside_temperature"}
        
        
#        self.check_system_msg = None
#        self.states = 0
#        self.flashing_states = 0

    def process(self, frame, mqtt_client, logger):
        pass
    
    def on_connect(client, data, flags, rc):
        for key, addr in self.topics.items():
            client.subscribe(addr, 1)


# # Will be called upon reception of CONNACK response from the server.
# def on_connect(client, data, flags, rc):
#     for key, addr in topics.items():
#         client.subscribe(addr, 1)

if __name__ == '__main__':

    broker="192.168.1.100"
    port=1883
    username="hkeene"
    password="homer4MQTT!"
    
    # Create dict for the info from pool
    pool_temp = {"pool_temperature": 12}
    spa_temp = {"spa_temperature": 23}
    outside_temp = {"outside_temperature": 80}

    logger = MyLogger()
    controller = AquaLogic()
    client = mqtt.Client("Pool1")
    client.on_connect = controller.on_connect
    #client.on_message = on_message
    client.username_pw_set(username, password)
    logger.log("Connecting to MQTT server")
    client.connect(broker, port, 60)

    time.sleep(1)
    client.loop_start()
    time.sleep(1)
    client.publish(controller.topics["pool_temperature_addr"], json.dumps(pool_temp, indent=4), 1)
    time.sleep(1)
    client.publish(controller.topics["spa_temperature_addr"], json.dumps(spa_temp, indent=4), 1)
    time.sleep(1)
    client.publish(controller.topics["outside_temperature_addr"], json.dumps(outside_temp, indent=4), 1)
    time.sleep(1)
    
    client.disconnect()