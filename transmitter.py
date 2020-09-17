from sys import byteorder
from enlace import enlace

MESSAGE_TYPE = [
  'err',
  'data',
  'handshake',
  'confirmation'
]

class Transmitter:
  def __init__(self, serialPort):
    self.com = enlace(serialPort)
    self.com.enable()
  
  def send(self, datagram):
    self.com.sendData(datagram)

  def receive(self, expected_type):
    head_status, (msg_type,
    msg_id,
    num_payloads,
    payload_index,
    payload_size,
    error_type,
    restart_index) = self.get_head()

    if not head_status:
      print('ERROR PARSING HEAD')
      return 0

    if MESSAGE_TYPE[msg_type] != expected_type:
      print('ENCOUNTERED AN ERROR:')
      print('EXPECTED {0} BUT RECEIVED {1}'.format(expected_type, MESSAGE_TYPE[msg_type]))
      return 0

    if MESSAGE_TYPE[msg_type] == 'err':
      print('ENCOUNTERED AN ERROR')
      return 0

    if MESSAGE_TYPE[msg_type] == 'data':
      print('RECEIVED PAYLOAD')
      payload_status, payload = self.get_payload(payload_size)
      if not payload_status:
        print('ERROR PARSING PAYLOAD')
        return 0
        
      if not self.get_EOP():
        return 0
      return(payload, payload_index, num_payloads)

    if MESSAGE_TYPE[msg_type] == 'handshake':
      print('RECEIVED HANDSHAKE')
      return self.get_EOP()

    if MESSAGE_TYPE[msg_type] == 'confirmation':
      print('RECEIVED CONFIRMATION')
      return self.get_EOP()

  def get_head(self):
    status, (head, size) = self.com.getData(10)
    
    if status == 0:
      print('CONNECTION TIMED OUT WHILE PARSING HEAD')
      return status, (0,0,0,0,0,0,0)
    
    msg_type = head[0]
    msg_id = head[1]
    num_payloads = int.from_bytes(head[2:4], byteorder)
    payload_index = int.from_bytes(head[4:6], byteorder)
    payload_size = head[6]
    error_type = head[7]
    restart_index = int.from_bytes(head[8:10], byteorder)
    return (status, 
      (
        msg_type,
        msg_id,
        num_payloads,
        payload_index,
        payload_size,
        error_type,
        restart_index
      )
    )

  def get_payload(self, size):
    status, (payload, sz) = self.com.getData(size)
    
    if status == 0:
      print('CONNECTION TIMED OUT WHILE PARSING PAYLOAD')
    
    return status, payload

  def get_EOP(self):
    status, (EOP, size) = self.com.getData(4)
    
    if status == 0:
      print('CONNECTION TIMED OUT WHILE PARSING EOP')
      return False
    
    candidate = int.from_bytes(EOP, byteorder)
    if candidate != 0:
      print("ERROR PARSING EOP")
      return False
    else:
      return True

  def disable(self):
    self.com.disable()