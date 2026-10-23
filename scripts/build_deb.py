#!/usr/bin/env python3
"""Wrap one validated queqiaopack Linux archive as an inactive CLI-only deb."""

import argparse
import datetime
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tarfile.open(args.archive, "r:gz") as archive:
        entries = {}
        total = 0
        root = None
        for member in archive:
            path = PurePosixPath(member.name)
            total += member.size
            if (not member.isfile() or path.is_absolute() or "\\" in member.name
                    or ".." in path.parts or len(path.parts) < 2
                    or member.size < 0 or total > 256 * 1024 * 1024
                    or len(entries) >= 4096):
                raise ValueError(f"unsupported archive member: {member.name!r}")
            root = root or path.parts[0]
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if path.parts[0] != root or relative in entries:
                raise ValueError("archive roots or entries are inconsistent")
            entries[relative] = archive.extractfile(member).read()

    info = dict(line.split("=", 1) for line in entries["BUILDINFO"].decode().splitlines())
    if info["target"] not in {"linux/amd64", "linux/arm64"} or info["wire_protocol"] != "1":
        raise ValueError("unsupported deb target or wire version")
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?", info["version"]):
        raise ValueError("unsupported package version")
    if not re.fullmatch(r"[0-9a-f]{40}", info["commit"]):
        raise ValueError("invalid source commit")
    arch = info["target"].split("/")[1]
    if root != f"queqiaod_{info['version']}_linux_{arch}":
        raise ValueError("archive root does not match BUILDINFO")
    if hashlib.sha256(entries["queqiaod"]).hexdigest() != info["binary_sha256"]:
        raise ValueError("binary checksum does not match BUILDINFO")
    date = datetime.datetime.fromisoformat(info["build_date"].replace("Z", "+00:00"))
    epoch = int(date.timestamp())
    version = info["version"][1:].replace("-", "~", 1)
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve() / f"queqiao_{version}_{arch}.deb"
    if output.exists():
        raise FileExistsError(output)

    with tempfile.TemporaryDirectory(prefix="queqiao-deb-") as temporary:
        stage = Path(temporary)
        binary = stage / "usr/bin/queqiaod"
        binary.parent.mkdir(parents=True)
        binary.write_bytes(entries.pop("queqiaod"))
        binary.chmod(0o755)
        docs = stage / "usr/share/doc/queqiao"
        for name, data in entries.items():
            target = docs.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(0o755 if name in {
                "deploy/install-client.sh", "deploy/install-server.sh", "deploy/tune-server.sh",
            } else 0o644)
        (docs / "copyright").write_bytes(entries["LICENSE"])
        control = stage / "DEBIAN/control"
        control.parent.mkdir()
        size = sum(p.stat().st_size for p in stage.rglob("*") if p.is_file())
        control.write_text(
            f"Package: queqiao\nVersion: {version}\nArchitecture: {arch}\n"
            "Section: net\nPriority: optional\nMaintainer: Queqiao contributors\n"
            "Depends: ca-certificates\nHomepage: https://github.com/acgq/queqiao\n"
            f"Installed-Size: {(size + 1023) // 1024}\n"
            "Description: Self-hosted TCP and UDP transport CLI\n"
            " Installs queqiaod with source metadata, SBOM, documentation and licenses.\n"
            " Configure client or gateway identity separately; no service is started.\n",
            encoding="utf-8", newline="\n",
        )
        control.chmod(0o644)
        for path in sorted(stage.rglob("*")):
            if path.is_dir():
                path.chmod(0o755)
            os.utime(path, (epoch, epoch))
        os.utime(stage, (epoch, epoch))
        subprocess.run([
            "dpkg-deb", "--root-owner-group", "--uniform-compression", "-Zxz", "-z9",
            "--build", str(stage), str(output),
        ], env=dict(os.environ, SOURCE_DATE_EPOCH=str(epoch)), check=True)
    print(output)


if __name__ == "__main__":
    main()
