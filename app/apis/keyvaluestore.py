import json
import time
import re
from json import JSONDecodeError
from typing import List, Any

from flask_restplus import Namespace, Resource, reqparse
from flask import current_app
from redis import Redis

api = Namespace(
    name='Redis KeyValue Store',
    description='Store Short Lived/Persistent Key-value data',
    path='/',
)

put_parser = reqparse.RequestParser()
put_parser.add_argument('expiry', type=int)
put_parser.add_argument('data', required=True, location="json")


@api.route('/keys', defaults={'id': None})
@api.route('/keys/<id>')
class KeyValueList(Resource):
    _hash = 'store'
    _expired_keys = 'expiry_keys'

    @api.response(200, 'Success.')
    @api.response(400, 'Bad Request')
    @api.doc(params={
        'filter': 'Add regex filter'
    })
    def get(self, id: str):
        """
        Returns the keys and values for specified id or all
        """
        redis_client: Redis = current_app.redis
        key_values = redis_client.hkeys(self._hash) if not id else [id.encode()]
        key_values = [key.decode() for key in key_values]
        filters = reqparse.request.args.get('filter')
        if filters:
            try:
                regex = re.compile(filters)
                key_values = list(filter(regex.match, key_values))
            except re.error:
                return 'Invalid Filter Regex', 400

        response = {
            key: self.get_value_by_key(redis_client, key)
            for key in key_values
        }
        if not any(response.values()):
            return '', 404
        return response, 200

    @api.response(200, 'Success.')
    @api.response(400, 'Bad Request')
    @api.expect(put_parser)
    def put(self, id: str):
        """
        Put a key-value mapping to redis.
        Request body should be a valid json string
        """
        redis_client: Redis = current_app.redis
        try:
            data: dict = json.loads(reqparse.request.data)
        except (ValueError, JSONDecodeError) as e:
            return "Bad Payload (Payload should be a valid json object", 400
        else:
            expiry_time = reqparse.request.args.get('expiry')
            for key, val in data.items():
                redis_client.hset(self._hash, key, val)
                if expiry_time:
                    redis_client.hset(self._expired_keys, key, time.time()+int(expiry_time))
            return "", 200

    @api.response(200, 'Success.')
    @api.response(404, 'Key Not Found')
    def delete(self, id: str):
        """
        Delete a specific key or all keys
        """
        redis_client: Redis = current_app.redis
        if id:
            if self.if_key_exists(redis_client, id):
                self.delete_keys(redis_client, id)
            else:
                return "Requested Key not found", 404
        else:
            self.delete_all(redis_client)

        return "", 200

    @api.response(200, 'Success.')
    @api.response(404, 'Key not found')
    def head(self, id: str):
        """
        Check if any key or any specific key presents
        """
        redis_client: Redis = current_app.redis
        keys_to_check = [id] if id else redis_client.hkeys(self._hash)
        is_present = [
            self.if_key_exists(redis_client, key)
            for key in keys_to_check
        ]
        if is_present and all(is_present):
            return "Key found in the store", 200
        return "No matching key found", 404

    def get_all_keys(self, rc: Redis) -> List:
        return rc.hgetall(self._hash)

    def if_key_exists(self, rc: Redis, key: str) -> bool:
        return rc.hexists(self._hash, key)

    def delete_keys(self, rc: Redis, key) -> bool:
        return rc.hdel(self._hash, key)

    def delete_all(self, rc: Redis) -> bool:
        _ = [self.delete_keys(rc, key) for key in self.get_all_keys(rc)]
        return True

    def get_all_key_values(self) -> Any:
        pass

    def get_value_by_key(self, rc: Redis, key: str) -> Any:
        val = rc.hget(self._hash, key)
        if val:
            return val.decode()
        return None

