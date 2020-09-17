import time
from os import path
import sys

from transmitter import Transmitter
from datagram import Datagram

SERIAL = "/dev/cu.usbmodem1421"

class Client:
  def __init__(self):
    self.message = bytes(0)
    self.transmitter = Transmitter(SERIAL)

  def set_message(self):
    # file = input('What file do you want to send? ')
    file='imgs/fofinha.png'
    
    while not path.exists(file):
      print("INVALID PATH")
      file = input('WHAT FILE DO YOU WANT TO SEND? ')
    
    with open(file, 'rb') as f:
      byte_file = f.read()

    self.message = byte_file

  def send_packet(self, payload, num_payloads, payload_index):
    packet = Datagram()
    packet.set_head(
      message_type=1,
      message_id=1,
      num_payloads=num_payloads,
      payload_index=payload_index,
      payload_size=len(payload),
      error_type=0,
      restart_index=0
    )
    packet.set_payload(payload=payload)
    packet.set_EOP(0)
    self.transmitter.send(packet.get_datagram())

  def receive_confirmation(self):
    return self.transmitter.receive(expected_type='confirmation')

  def send_handshake(self):
    packet = Datagram()
    packet.set_head(
      message_type=2,
      message_id=1,
      num_payloads=0,
      payload_index=0,
      payload_size=0,
      error_type=0,
      restart_index=0
    )
    packet.set_EOP()
    self.transmitter.send(packet.get_datagram())

  def assert_server_status(self):
    self.send_handshake()
    print('ASSERTING SERVER CONNECTION')

    confirmed = self.receive_confirmation()
    while not confirmed:
      print('SERVER DISCONNECTED')
      retry = input('RETRY CONNECTION? (y/n) ')
      if retry == 'y':
        self.send_handshake()
        print('ASSERTING SERVER CONNECTION')
        confirmed = self.receive_confirmation()
      else:
        self.disable()
        sys.exit()

    print('SERVER AWAKE')

  def send_message(self):
    num_bytes = len(self.message)
    num_packets = num_bytes // 114 + 1 if num_bytes % 114 != 0 else num_bytes // 114

    print('BEGINNING TRANSMISSION')
    print('BYTES TO SEND: {}'.format(num_bytes))
    print('NUMBER OF PAYLOADS: {}'.format(num_packets))

    for i in range(1, num_packets+1):
      payload = self.message[(i-1)*114 : i*114]
      
      self.send_packet(
        payload=payload,
        payload_index=i,
        num_payloads=num_packets
      )

      if not self.receive_confirmation():
        break

  def disable(self):
    self.transmitter.disable()
      
  
client = Client()
client.set_message()
client.assert_server_status()
client.send_message()
client.disable()