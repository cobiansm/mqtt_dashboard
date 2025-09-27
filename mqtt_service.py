import paho.mqtt.client as mqtt
from typing import Callable, Dict, Optional

class MqttService:

    def __init__(self,
                 host: str = "localhost",
                 port: int = 1883,
                 keepalive: int = 60,
                 log_fn: Optional[Callable[[str], None]] = None):
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self._log = log_fn or (lambda m: None)
        self._client = mqtt.Client()
        self._handlers: Dict[str, Callable[[str, str], None]] = {}

        # callbacks 
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

    # ------------------- API -------------------
    def start(self):
        try:
            self._client.connect_async(self.host, self.port, self.keepalive)
            self._client.loop_start()
            self._log(f"MQTT -> starting connection {self.host}:{self.port}")
        except Exception as e:
            self._log(f"MQTT start error: {e}")

    def stop(self):
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:
            pass

    def publish(self, topic: str, payload, qos: int = 1, retain: bool = True):
        try:
            self._client.publish(topic, payload=payload, qos=qos, retain=retain)
        except Exception as e:
            self._log(f"MQTT publish error {topic}: {e}")

    def subscribe(self, topic: str, handler: Callable[[str, str], None], qos: int = 1):
        self._handlers[topic] = handler
        try:
            self._client.subscribe(topic, qos=qos)
            self._log(f"MQTT subscribed to {topic}")
        except Exception as e:
            self._log(f"MQTT subscribe error {topic}: {e}")

    # ------------------- Internal callbacks -------------------
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._log("MQTT connected (rc=0)")
            # Re-suscribir tópicos registrados tras reconexión
            for t in self._handlers.keys():
                try:
                    client.subscribe(t)
                except Exception as e:
                    self._log(f"Re-sub error {t}: {e}")
        else:
            self._log(f"MQTT connection failed rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self._log(f"MQTT unexpected disconnection rc={rc}")
        else:
            self._log("MQTT disconnected")

    def _on_message(self, client, userdata, msg):
        handler = self._handlers.get(msg.topic)
        if handler:
            try:
                payload = msg.payload.decode("utf-8", errors="replace").strip()
                handler(msg.topic, payload)
            except Exception as e:
                self._log(f"Handler error {msg.topic}: {e}")
