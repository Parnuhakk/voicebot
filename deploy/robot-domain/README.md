# Robot-only website

`https://robot.arleserver.cfd/` is the only published Voicebot website. Its
restaurant reception includes table reservations, restaurant information and
the text/microphone demo behind the existing operator authorization.

Use the existing Coolify application's `https://robot.arleserver.cfd` domain.
No additional website, custom router, container or DNS record is required.
Preserve the original `/data` volume, restaurant identity, bookings/history,
voice configuration and automatic GitHub deployment.

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

- Robot `/`, `/health`, versioned assets and `/api/public/restaurant`: HTTP 200.
- Robot navigation has no links to the retired hostname. Existing restaurant,
  demo and microphone controls remain present.
- Robot private `/api/bookings`, `/api/calls` and `/api/call-history` without
  authorization: HTTP 403 with `Cache-Control: no-store`.
- Robot `/hotel` and `/hotel/`: HTTP 410, no redirect.
- Meretuule root, assets and APIs: unavailable; neither website content nor a
  redirect to Voicebot is served. An unrouted hostname may return the ingress
  error rather than the application's HTTP 410.
- Run `tests/robot_domain_browser_checks.js` separately for read-only public
  browser acceptance; `tests/run_browser_checks.cjs` runs local fixture checks.
