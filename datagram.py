from sys import byteorder

class Datagram:
  def __init__(self):
    self.head = bytes(10)
    self.payload = bytes(0)
    self.EOP = bytes(4)

  def set_head(
    self, 
    message_type,
    message_id,
    num_payloads,
    payload_index,
    payload_size,
    error_type,
    restart_index
  ):
    self.head = (
      int(message_type).to_bytes(1, byteorder) +
      int(message_id).to_bytes(1, byteorder) +
      int(num_payloads).to_bytes(2, byteorder) +
      int(payload_index).to_bytes(2, byteorder) +
      int(payload_size).to_bytes(1, byteorder) +
      int(error_type).to_bytes(1, byteorder) +
      int(restart_index).to_bytes(2, byteorder)
    )
    
  def set_payload(self, payload):
    self.payload = payload

  def set_EOP(self, eop=0):
    self.EOP = (eop).to_bytes(4, byteorder)

  def get_datagram(self):
    return self.head+self.payload+self.EOP


"""

HEAD:
{
  Message type: 1 Byte
  Message id: 1 Byte
  Num payloads: 2 Bytes
  Payload index: 2 Bytes
  Payload size: 1 Byte
  Error type: 1 Byte
  Where to Restart: 2 Bytes
}

"""

