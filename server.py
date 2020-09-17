from os import path
import time

from transmitter import Transmitter
from datagram import Datagram

SERIAL = "/dev/cu.usbmodem1411"

class Server:
  def __init__(self):
    self.message = bytes(0)
    self.transmitter = Transmitter(SERIAL)
    self.location = 'imgs/foto_nova.png'

  def set_location(self):
    # name = input('SPECIFY NAME TO SAVE FILE WITHOUT EXTENSION: ')
    name = 'foto_new2'
    while len(name) < 1:
      print('INVALID FILE NAME')
      name = input('SPECIFY NAME TO SAVE FILE WITHOUT EXTENSION: ')
    self.location = 'imgs/{}.png'.format(name)

  def send_confirmation(self):
    packet = Datagram()
    packet.set_head(
      message_type=3,
      message_id=1,
      num_payloads=0,
      payload_index=0,
      payload_size=0,
      error_type=0,
      restart_index=0
    )
    packet.set_EOP()
    self.transmitter.send(packet.get_datagram())

  def confirm_handshake(self):
    handshake_received = self.transmitter.receive(expected_type='handshake')
    print(handshake_received)
    while not handshake_received:
      print('HANDSHAKE NOT SENT BY CLIENT - LISTENING ON SERIAL PORT {}'.format(SERIAL))
      handshake_received = self.transmitter.receive(expected_type='handshake')
    print('HANDSHAKE RECEIVED')
    self.send_confirmation()
    print('HANDSHAKE CONFIRMED')

  def send_error(self):
    packet = Datagram()
    packet.set_head(
      message_type=0,
      message_id=1,
      num_payloads=0,
      payload_index=0,
      payload_size=0,
      error_type=0,
      restart_index=0
    )
    packet.set_EOP()
    self.transmitter.send(packet.get_datagram())

  def receive_packet(self):
    response = self.transmitter.receive(expected_type='data')
    if not response:
      return 0
    return response # response => tuple(payload, payload_index, num_packets)

  def receive_message(self):
    buffer = bytes()
    last_payload = 0
    while True:
      response = self.receive_packet()
      if not response:
        print('ENCOUNTERED ERROR RECEIVING DATA')
        self.send_error()
        break

      (payload, payload_index, num_packets) = response
      
      if payload_index != last_payload + 1:
        print('PAYLOAD OUT OF ORDER')
        self.send_error()
        break

      last_payload = payload_index

      buffer += payload
      self.send_confirmation()
      print('\n\n\n')
      print(buffer)
      print(payload_index, num_packets)
      print('\n\n\n')

      if payload_index == num_packets:
        break

    with open(self.location, 'wb') as f:
      f.write(buffer)

  def disable(self):
    self.transmitter.disable()


server = Server()
server.set_location()
server.confirm_handshake()
server.receive_message()
server.disable()