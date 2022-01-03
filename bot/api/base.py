import aiohttp
from loguru import logger
from pydantic import parse_obj_as
import io
from datetime import datetime

from config import BACKEND_URL

success_codes = (200, 201, 204)


async def request(req_type : str, path : str, json : dict=None, data : dict=None, query : dict=None):
    if not path.endswith('/'):
        path += '/'
    if query:
        path += '?' + '&'.join([ f'{k}={v}' for k, v in query.items() ])
    url = 'http://' + BACKEND_URL + '/api/v1/' + path
    logger.debug(f"URL FOR REQUEST: {url}")
    logger.debug(data)
    response_json = None
    status_code = None

    if json is not None:
        json = { k: v if not isinstance(v, datetime) else v.isoformat() for k, v in json.items() }
        json = { k: v for k, v in json.items() if v is not None }

    if req_type == 'get':
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as resp:
                logger.debug(f"API_UTILS: GET-request. resp status code: {resp.status}")
                status_code = resp.status
                response_json = await resp.json()
    elif req_type == 'post':
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.post(url, json=json, data=data) as resp:
                logger.debug(f"API_UTILS: POST-request. resp status code: {resp.status}")
                status_code = resp.status
                response_json = await resp.json()
    elif req_type == 'patch':
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.patch(url, json=json, data=data) as resp:
                logger.debug(f"API_UTILS: PATCH-request. resp status code: {resp.status}")
                status_code = resp.status
                response_json = await resp.json()
    elif req_type == 'delete':
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.delete(url, json=json, data=data) as resp:
                logger.debug(f"API_UTILS: DELETE-request. resp status code: {resp.status}")
                status_code = resp.status
                # response_json = await resp.json()
    else:
        raise ValueError('Unknown request type')

    logger.debug(f"{url} {response_json=} {status_code=}")
    if status_code not in success_codes:
        return None
    else:
        return response_json


async def get_instance(obj_type, *args, **kwargs):
    response_json = await request(*args, **kwargs)
    if response_json is None:
        raise ValueError('Failed request')
    return parse_obj_as(obj_type, response_json)


async def get_image(url):
    if url.startswith('/'):
        url = 'http://' + BACKEND_URL + url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            logger.info(f'Getting picture')
            logger.info(f"Response status code: {resp.status}")
            picture_bytes = await resp.read()
            picturefile = io.BytesIO()
            picturefile.write(picture_bytes)
            picturefile.seek(0)
    return picturefile