import asyncio
import json
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import aiosqlite
import uvicorn  
from uvicorn import lifespan
import uuid
import socket
from sqlops import createdb, deletedb

DB_PATH = "users.db"
UNITY_HOST = "127.0.0.1"
UNITY_PORT = 9000

RATE_LIMIT_SECONDS = 0.25
last_seen = {}
USERS_PER_IP = 10

COMMAND_QUEUE = asyncio.Queue()

async def send_to_unity():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        cmd = await COMMAND_QUEUE.get()
        try:
            message = (json.dumps(cmd) + "\n").encode()
            sock.sendto(message, (UNITY_HOST, UNITY_PORT))
        except Exception as e:
            print(f"[ERROR] Sending to Unity failed: {e}")
        await asyncio.sleep(0.01)

async def get_user(username):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT uuid, ip FROM users WHERE username=?", (username,)) as cursor:
            row = await cursor.fetchone()
            return row

async def add_new_user(username, ip):
    new_uuid = str(uuid.uuid4())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO users (username, uuid, ip) VALUES (?, ?, ?)", (username, new_uuid, ip))
        await db.commit()
    return new_uuid

def check_rate_limit(ip):
    now = time.time()
    if ip in last_seen and (now - last_seen[ip]) < RATE_LIMIT_SECONDS:
        return False
    last_seen[ip] = now
    return True

async def check_user_ip_limit(ip):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE ip=?", (ip,)) as cursor:
            row = await cursor.fetchone()
            return row[0] < USERS_PER_IP

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    deletedb()
    createdb()

    asyncio.create_task(send_to_unity())
    print("[INFO] Unity UDP sender started")

@app.post("/control")
async def control(request: Request):
    client_ip = request.client.host
    data = await request.json()

    username = data.get("username")
    command = data.get("command")
    params = data.get("params", {})

    if not username or not command:
        raise HTTPException(status_code=400, detail="Missing username or command")

    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    if not await check_user_ip_limit(client_ip):
        raise HTTPException(status_code=429, detail="User Limit Per IP Reached")

    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=403, detail="Unknown user")

    users_uuid, ip = user
    if client_ip != ip:
        raise HTTPException(status_code=403, detail="IP mismatch")

    await COMMAND_QUEUE.put({
        "username": username,
        "uuid": users_uuid,
        "command": command,
        "params": params
    })

    return JSONResponse({"status": "ok","message": "Command enqueued",  "uuid": users_uuid, "command": command, "params": params})

@app.post("/create")
async def create(request: Request):
    client_ip = request.client.host
    data = await request.json()
    if not check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    username = data.get("username")
    user = await get_user(username)
    if user is not None:
        raise HTTPException(status_code=403, detail="User already exists")
    new_uuid = await add_new_user(username, client_ip)
    
    params = data.get("params", {})

    await COMMAND_QUEUE.put({
        "username": username,
        "uuid": new_uuid,
        "command": "create",
        "params": params
    })

    return JSONResponse({"status": "ok", "message": "User created" , "uuid": new_uuid , "ip": client_ip , "username": username})
    
@app.post("/remove")
async def remove(request: Request):
    client_ip = request.client.host
    data = await request.json()

    username = data.get("username")
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=403, detail="Unknown user")

    users_uuid, ip = user
    if client_ip != ip:
        raise HTTPException(status_code=403, detail="IP mismatch")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE username=? AND ip=?", (username, client_ip))
        await db.commit()

    await COMMAND_QUEUE.put({
        "username": username,
        "uuid": users_uuid,
        "command": "remove",
        "params": {}
    })

    return JSONResponse({"status": "ok", "message": "User removed", "username": username})

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
