import asyncio
import json

HOST = '127.0.0.1'
PORT = 9000

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[INFO] Connection from {addr}")

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            data = line.decode().strip()
            print(f"[RECV] {data}")

            # Optional: parse JSON to check structure
            try:
                obj = json.loads(data)
                print(f"  Parsed command: {obj.get('command')} for UUID {obj.get('uuid')}")
            except json.JSONDecodeError:
                print("  [ERROR] Invalid JSON")
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    print(f"[INFO] Connection closed: {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"[INFO] Debug TCP server listening on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
