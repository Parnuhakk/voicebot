# Restobot website and robot compatibility

`https://restobot.arleserver.cfd/` is the canonical Voicebot website. The public
landing shares the operator workspace's style. `/dashboard` combines the table
calendar, stored bookings, text/microphone demo and restaurant information with
one operator connection. `/dashboard#calendar-section` opens the calendar;
the former calendar page and slash aliases redirect there with queries preserved.
Stored bookings, occupancy and the text/microphone demo retain operator authorization.

Use the existing Coolify application domains
`https://restobot.arleserver.cfd,https://robot.arleserver.cfd`.
No additional website, custom router, container or DNS record is required.
Preserve the original `/data` volume, restaurant identity, bookings/history,
voice configuration and automatic GitHub deployment.

## Hostname migration

On the Arle host, wildcard DNS and the Cloudflare application tunnel already
route both names to Traefik; no tunnel/DNS change is necessary. Update Coolify's
application domain setting (not only its generated Compose file), then deploy
the verified release. Do not restart shared proxy/tunnel services.

Old robot browser pages return HTTP 308 to the same Restobot path/query. Health,
private APIs and carrier callbacks remain on the old host for compatibility;
POSTs and WebSockets are never cross-domain redirects. The separate Twilio
bridge publishes both exact hosts at priority 10000, emits the canonical
Restobot media URL and accepts signatures only for the finite old/new origin
allowlist. Switch the existing carrier webhook to the canonical URL after
Restobot's bridge route is reachable. This is not proof of a real carrier call.

## Retire the former Meretuule publication

The separate `meretuule.arleserver.cfd` website is removed. After inspecting the
installed file, delete only its dedicated Traefik configuration:

```bash
sudo rm -- /data/coolify/proxy/dynamic/meretuule.yml
```

This removes both the second website router and the old robot `/hotel`
redirect. Keep any backup outside Traefik's watched directory. Do not reinstall
the retired configuration or add the hostname to Coolify's application domains.
Traefik reloads dynamically; do not restart shared proxy/tunnel services.

The shared wildcard DNS/tunnel may still resolve the retired hostname. Leave
that infrastructure intact for other applications; resolution is not website
publication. The application also returns HTTP 410 for that exact hostname,
including its assets and APIs, if a fallback route forwards it.

## Verify

- Restobot `/`, `/dashboard`, `/health`, versioned
  assets and `/api/public/restaurant`: HTTP 200.
- `/booking-calendar`, `/booking-calendar/` and `/booking-calendar.html`: HTTP 308
  to `/dashboard` with the original query and `#calendar-section`.
- Old robot browser pages: HTTP 308 preserving path/query; old `/health`: HTTP 200.
- Restobot navigation has no links to the retired hostname. Existing restaurant,
  demo and microphone controls remain present.
- Both hosts' private `/api/bookings`, `/api/calls` and `/api/call-history` without
  authorization: HTTP 403 with `Cache-Control: no-store`.
- Robot `/hotel` and `/hotel/`: HTTP 410, no redirect.
- Meretuule root, assets and APIs: unavailable; neither website content nor a
  redirect to Voicebot is served. An unrouted hostname may return the ingress
  error rather than the application's HTTP 410.
- Run `tests/robot_domain_browser_checks.js` separately for read-only public
  browser acceptance; `tests/run_browser_checks.cjs` runs local fixture checks.
