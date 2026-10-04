"""Ingress boot policy, including real systemd success/failure transactions."""

import configparser
import os
import shlex
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

UNIT_DIR = Path(
    os.environ.get(
        "VOICEBOT_BOOT_UNIT_DIR", Path(__file__).resolve().parents[1] / "deploy/host"
    )
)
PROXY = "vps-migrated-proxy.service"
TUNNEL = "cloudflared-home-apps.service"
UNRELATED = {
    "vps-migrated-apps.service",
    "vps-migrated-control.service",
    "vps-migrated-workers.service",
}


def dependencies(name):
    config = configparser.ConfigParser(interpolation=None)
    config.read(UNIT_DIR / name)
    return {
        key: config["Unit"].get(key, "").split()
        for key in ("Requires", "Wants", "After")
    }


def test_ingress_boot_policy_does_not_pull_unrelated_workloads():
    for name, required in ((PROXY, "docker.service"), (TUNNEL, PROXY)):
        deps = dependencies(name)
        assert not UNRELATED.intersection(set().union(*deps.values())), name
        assert required in deps["Requires"] and required in deps["After"], name
        assert "network-online.target" in deps["Wants"], name
        assert "network-online.target" in deps["After"], name
        assert not {"network-online.target", "terrapoint-ingress.service"}.intersection(
            deps["Requires"]
        ), name
    assert "terrapoint-ingress.service" in dependencies(TUNNEL)["Wants"]


@pytest.mark.parametrize("docker_status", [0, 17])
def test_proxy_boot_reuses_existing_container_and_preserves_docker_failure(
    tmp_path, docker_status
):
    config = configparser.ConfigParser(interpolation=None)
    config.read(UNIT_DIR / PROXY)
    command = shlex.split(config["Service"]["ExecStart"])
    assert command[0] == "/usr/bin/docker", (
        "boot must not redeploy legacy Compose networks"
    )
    docker = tmp_path / "docker"
    docker.write_text(
        "#!/bin/sh\n"
        'if [ "$#" -ne 2 ] || [ "$1" != start ] || [ "$2" != coolify-proxy ]; then\n'
        "  exit 23\n"
        "fi\n"
        'exit "$FIXTURE_DOCKER_STATUS"\n'
    )
    docker.chmod(0o755)
    command[0] = str(docker)
    result = subprocess.run(
        command,
        env={"PATH": "/usr/bin:/bin", "FIXTURE_DOCKER_STATUS": str(docker_status)},
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == docker_status


@pytest.mark.parametrize("proxy_succeeds", [True, False])
def test_real_startup_ignores_optional_failures_but_requires_working_proxy(
    proxy_succeeds,
):
    if not shutil.which("systemd-run") or not shutil.which("systemctl"):
        pytest.skip("systemd tools unavailable")
    # Isolated user-manager fixtures: never start/stop production system units.
    runtime = f"/run/user/{os.getuid()}"
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(Path.home()),
        "XDG_RUNTIME_DIR": runtime,
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path={runtime}/bus",
    }
    available = subprocess.run(
        ["systemctl", "--user", "show", "default.target", "--property=ActiveState"],
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )
    if available.returncode:
        pytest.skip("running user systemd manager unavailable")

    policy = {name: dependencies(name) for name in (PROXY, TUNNEL)}
    prerequisites = set(UNRELATED)
    for deps in policy.values():
        prerequisites.update(*deps.values())
    prerequisites.difference_update((PROXY, TUNNEL))
    prefix = "voicebot-boot-test-" + uuid.uuid4().hex[:10]
    names = {
        name: f"{prefix}-{Path(name).stem}.service"
        for name in prerequisites | {PROXY, TUNNEL}
    }
    created = []

    def start(name, succeeds, deps=None):
        created.append(names[name])
        argv = [
            "systemd-run",
            "--user",
            "--quiet",
            "--unit=" + names[name],
            "--property=Type=oneshot",
            "--property=RemainAfterExit=yes",
        ]
        for key, values in (deps or {}).items():
            if values:
                argv.append(
                    "--property=" + key + "=" + " ".join(names[v] for v in values)
                )
        argv.append("/usr/bin/true" if succeeds else "/usr/bin/false")
        return subprocess.run(
            argv, env=env, capture_output=True, check=False, text=True, timeout=15
        )

    try:
        for name in sorted(prerequisites):
            succeeds = name == "docker.service"
            result = start(name, succeeds)
            assert (result.returncode == 0) == succeeds, result.stderr
        proxy = start(PROXY, proxy_succeeds, policy[PROXY])
        assert (proxy.returncode == 0) == proxy_succeeds, proxy.stderr
        tunnel = start(TUNNEL, True, policy[TUNNEL])
        assert (tunnel.returncode == 0) == proxy_succeeds, tunnel.stderr
    finally:
        for action in ("stop", "reset-failed"):
            subprocess.run(
                ["systemctl", "--user", action, *created],
                env=env,
                capture_output=True,
                check=False,
                timeout=15,
            )
