# Remote Server Docker Scaffolding

This setup lets you run `browser-use` as a remote browser agent host in Docker (Mac/Windows via Docker Desktop), with optional:

- **Persistent profiles** (saved under `./data` on the host)
- **Ephemeral profiles** (no persistence; data lives only in container memory)
- **Cloudflared tunnel** to expose the service to the internet

## Files

- `docker-compose.yml` – main service (`browseruse`)
- `docker-compose.ephemeral.yml` – override to make browser data ephemeral
- `docker-compose.tunnel.yml` – Cloudflared tunnel sidecar (optional)

## 1. Build the image

From the `browser-use` repo root (same folder as `Dockerfile`):

```bash
# Mac / Linux
docker compose build browseruse

# Windows PowerShell
docker compose build browseruse
```

This uses the existing `Dockerfile` to build an image named `browseruse-local`.

## 2. Run with persistent profiles

Mounts `./data` on the host to `/data` in the container. Browser profiles and cookies persist between runs.

```bash
# Mac / Windows (Docker Desktop)
BROWSER_USE_API_KEY=your_key docker compose up browseruse
```

- Connect to the browser CDP endpoint on `localhost:9222` from your agent code.
- `BROWSER_USE_PROFILE_NAME` (optional) chooses which profile under `/data/profiles/` to use; default is `default`.

## 3. Run with ephemeral profiles (no persistence)

Use the ephemeral override so `/data` is a tmpfs inside the container.

```bash
# Mac / Windows
BROWSER_USE_API_KEY=your_key docker compose \
  -f docker-compose.yml \
  -f docker-compose.ephemeral.yml \
  up browseruse
```

- All browser data is discarded when the container stops.

## 4. Expose via Cloudflared tunnel (internet-accessible endpoint)

You need a **Cloudflare Tunnel token**.

1. Create a tunnel in your Cloudflare account and get the `TUNNEL_TOKEN`.
2. Run with the tunnel sidecar:

```bash
# Mac / Windows
$env:BROWSER_USE_API_KEY="your_key"       # Windows PowerShell example
$env:CLOUDFLARE_TUNNEL_TOKEN="your_token"

docker compose \
  -f docker-compose.yml \
  -f docker-compose.tunnel.yml \
  up browseruse tunnel
```

Cloudflared will expose the `browseruse` container on an HTTPS URL configured in your Cloudflare tunnel (e.g. `https://my-bu-server.yourdomain.com`).

## 5. How to use as a remote endpoint

- Point your **remote agent** or **MCP server** at the CDP endpoint of this container.
- Use the Cloudflare URL if the agent runs outside your LAN; otherwise use `localhost:9222` from the host.
- Choose persistence mode by selecting either:
  - `docker-compose.yml` only (persistent), or
  - `docker-compose.yml` + `docker-compose.ephemeral.yml` (ephemeral).
