import json
import sys


class DataPacket:
    """ This is a base class that provides JSON serialization for data packets to be sent between server and clients.
    The load_packet method converts the sent dictionaries back to their original DataPacket objects."""

    @staticmethod
    def load_packet(packet: bytes) -> object:
        d = json.loads(packet.decode('utf-8'))
        d['__class__'] = getattr(sys.modules[__name__], d['__class__'])
        instance = object()

        for key, value in d.items():
            setattr(instance, key, value)

        return instance

    def to_dict(self):

        #  Populate the dictionary with object meta data
        obj_dict = {
            '__class__': self.__class__.__name__
        }

        #  Populate the dictionary with object properties
        obj_dict.update(self.__dict__)

        return obj_dict

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_bytes(self):
        return bytes(self.to_json(), 'utf-8')
