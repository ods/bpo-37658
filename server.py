# Based on https://gist.github.com/hexrain/bc92aa70eebc229365f0ce4bcccf7fc4

import asyncio
import ssl


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    print("Send: %r" % message)
    writer.write(data)
    await writer.drain()


async def main():
    sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sc.load_cert_chain('localhost.crt', 'localhost.key')

    server = await asyncio.start_server(handle_echo, '127.0.0.1', 5000, ssl=sc)
    async with server:
        await server.serve_forever()


asyncio.run(main())
