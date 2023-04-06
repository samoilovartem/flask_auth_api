from orjson import dumps, loads


class ORJSONDecoder:
    @staticmethod
    def decode(data):
        """
        Decode the given data using orjson.loads.
        """
        try:
            return loads(data)
        except Exception as e:
            raise ValueError(f'Error decoding data: {e}') from e


class ORJSONEncoder:
    @staticmethod
    def encode(data):
        """
        Encode the given Python object using orjson.dumps.
        """
        try:
            return dumps(data).decode('utf-8')
        except Exception as e:
            raise ValueError(f'Error encoding object: {e}') from e
