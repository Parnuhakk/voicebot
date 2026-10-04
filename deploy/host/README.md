# Arle host ingress boot recovery

These are the existing Arle host units with their boot dependencies and proxy
startup corrected. They are host-specific, not a new application deployment. Publishing
this repository does not install them; review and install them on the host.

After the 2026-10-04 restart, a missing migrated Chatwoot image made
`vps-migrated-apps.service` fail. Both ingress units required that unrelated
stack, so systemd never started the application tunnel. Voicebot and Traefik
containers had already restarted normally. The public symptom was Cloudflare
error 1033 despite healthy local Voicebot containers.

A clean startup also exposed an obsolete external network in the legacy proxy
Compose project. Boot now starts the existing `coolify-proxy` container directly,
without redeploying Compose, pulling images or recreating retired networks.
The existing container, mounts, network attachments and loopback bindings stay
intact. This deliberately requires that already-provisioned container; first-time
proxy deployment remains a separate host operation.

The proxy now requires Docker, not Chatwoot, n8n or Coolify control/data startup.
The tunnel requires the proxy; Terrapoint ingress remains a soft dependency.
Tunnel commands, credential-file handling, hardening and restart policy
are unchanged. Proxy stop also targets only the existing container. Preserve
existing drop-ins, particularly the IPv4 network
stability setting. Never copy credential contents into this repository.

## Install the reviewed units

Run from the verified checkout on the Arle host. First compare these files with
the installed units: preserve any subsequent service-command or hardening
changes. Removing dependency lists requires editing/replacing the complete
unit; empty `Requires=`, `Wants=` or `After=` drop-in assignments do not clear them.

```bash
backup="/var/backups/voicebot-ingress/$(date -u +%Y%m%dT%H%M%SZ)"
sudo install -d -m 0700 "$backup"
sudo cp -p /etc/systemd/system/vps-migrated-proxy.service /etc/systemd/system/cloudflared-home-apps.service "$backup/"
sudo systemd-analyze verify deploy/host/vps-migrated-proxy.service deploy/host/cloudflared-home-apps.service
sudo install -m 0644 deploy/host/vps-migrated-proxy.service deploy/host/cloudflared-home-apps.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vps-migrated-proxy.service cloudflared-home-apps.service
sudo systemctl restart cloudflared-home-apps.service
```

This briefly reconnects shared application ingress. It does not restart
Voicebot/database containers, replace data volumes, change DNS, or start the
migrated applications/workers. Do not restore the missing Chatwoot image as a
Voicebot fix. An unrelated migrated-app failure can remain independently.

## Verify

```bash
python -m pytest -q tests/test_host_boot_dependencies.py
systemctl show vps-migrated-proxy.service cloudflared-home-apps.service --property=ActiveState,SubState,UnitFileState,Requires,Wants,After
systemctl is-active docker.service vps-migrated-proxy.service cloudflared-home-apps.service
systemctl is-enabled vps-migrated-proxy.service cloudflared-home-apps.service
```

Tests use parsed unit policy and uniquely named user-systemd fixtures to prove
that unrelated/soft dependency failures do not block ingress, but a genuine proxy
failure still blocks the tunnel. Runtime fixtures skip when no user manager is
available; the dependency-policy check always runs. No production units or
containers are stopped by the tests. A Docker command double additionally checks
that boot reuses the existing proxy and propagates a nonzero Docker exit status.

Verify `https://restobot.arleserver.cfd/`, `/dashboard`, `/health` and
`/api/public/restaurant` with a real browser. Local Twilio bridge `/health` and
LiveKit worker `/` must return HTTP 200. Keep unauthenticated operator APIs
forbidden; do not place paid calls or create bookings as readiness probes.
Exercise ordinary tunnel restart with migrated apps still failed, and compare
container identities/mounts and unrelated service states before/after. This is
boot-equivalent service verification, not a claim that the whole host rebooted.
