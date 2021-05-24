# Script to demonstrate how circular references cause to flaky errors

import asyncio
import gc
import ssl

import objgraph


class MyEchoClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        print('connection_made', transport)
        query = 'hello world'
        transport.write(query.encode())

    def data_received(self, data):
        print('data_received', data)

    def connection_lost(self, exc):
        print('connection_lost', exc)


async def test():
    loop = asyncio.get_event_loop()
    sc = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='localhost.crt')
    sc.check_hostname = False
    sc.verify_mode = ssl.CERT_NONE
    connector = loop.create_connection(MyEchoClientProtocol, '127.0.0.1', 5000, ssl=sc)
    res = await connector
    print(res)


culprit_types = [
    'asyncio.selector_events._SelectorSocketTransport',
    'asyncio.sslproto._SSLProtocolTransport',
]

def print_graph():
    # Uncommenting the following line changes the order of desctrucor calls
    # causing the error to disappear:
    # culprit_types.reverse()
    targets = []
    for culprit_type in culprit_types:
        targets += objgraph.by_type(culprit_type)
        gc.collect(1)
    print(f'Targets: {len(targets)}')
    objgraph.show_backrefs(targets, filename='ssl_circular_refs.png', max_depth=10)


print('Start')
gc.disable()
asyncio.run(test())
print_graph()
print('before collect')
gc.collect()
print('The end')
