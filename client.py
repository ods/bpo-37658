# Based on https://bugs.python.org/file48500/example.py

import asyncio
import ssl


class MyEchoClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        print('connection_made', transport)
        query = 'hello world'
        transport.write(query.encode())

    def data_received(self, data):
        print('data_received', data)

    def connection_lost(self, exc):
        print('connection_lost', exc)


async def create_connection(ssl_obj):
    loop = asyncio.get_event_loop()
    connector = loop.create_connection(MyEchoClientProtocol, '127.0.0.1', 5000, ssl=ssl_obj)
    connector = asyncio.ensure_future(connector)
    try:
        tr, pr = await connector
    except asyncio.CancelledError:
        if connector.done():
            tr, pr = connector.result()
            # Uncommenting the following line fixes the problem:
            # tr.close()
        raise
    return tr, pr


async def main(timeout, ssl_obj):
    return await asyncio.wait_for(create_connection(ssl_obj), timeout=timeout)


async def test_cancel():
    sc = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='localhost.crt')
    sc.check_hostname = False
    sc.verify_mode = ssl.CERT_NONE
    for _ in range(100):
        timeout = 0.002
        try:
            tr, pr = await main(
                timeout=timeout, ssl_obj=sc
            )
            tr.close()
        except asyncio.TimeoutError as e:
            print('timeouterror', repr(e))
    await asyncio.sleep(5)


asyncio.run(test_cancel())
