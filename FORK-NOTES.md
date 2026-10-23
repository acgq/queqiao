# Fork extensions

This file describes local extensions without changing upstream documentation.

## Development installation packages

The **deb and Windows packages** Actions workflow can be run manually for an
exact source commit. Its artifact includes amd64/arm64 Debian packages,
unsigned Windows executables, portable archives, checksums, SBOMs and licenses.
These are development builds, not signed public releases. Windows retains its
testing status described in `docs/STATUS.md`.

The Debian package installs `/usr/bin/queqiaod` and documentation under
`/usr/share/doc/queqiao`. It does not create an identity, open a proxy listener,
or enable a service. Configure the client or gateway using the bundled
deployment instructions after installing with `sudo apt install ./queqiao_*.deb`.
Use the package matching the machine's architecture. Verify the artifact's
`INSTALLER-SHA256SUMS` before installation.

`scripts/build_deb.py` wraps a Linux archive generated and validated by
`cmd/queqiaopack`; it preserves its BUILDINFO, SBOM and dependency licenses.
For example, on Linux with `dpkg-deb`:

```sh
python3 scripts/build_deb.py /path/to/queqiaod_VERSION_linux_amd64.tar.gz \
  --output /path/to/new-deb-output
```

## QUIC version selection

Native clients prefer QUIC v2 and retain v1 for version negotiation. The
Queqiao wire protocol and ALPN remain version 1, with unchanged mutual TLS.

For a path that rewrites QUIC v1 Initials as HTTP/3, a gateway can use
`queqiaod server --state /var/lib/queqiao/provider --quic-v2-only`. This makes
clients supporting both versions negotiate v2 before TLS. It is off by
default; a client without QUIC v2 needs the gateway's TLS/TCP fallback.
Removing the option restores acceptance of both carrier versions. Do not
enable it on a QUIC-only deployment with clients that support only QUIC v1.

## SOCKS5 egress

`queqiaod server --state /var/lib/queqiao/provider --outbound-socks5 127.0.0.1:1080`
routes destination TCP and UDP through a trusted local SOCKS5 router. The
router must support unauthenticated CONNECT and UDP ASSOCIATE on loopback.
There is no silent direct fallback. Queqiao validates current destination
addresses before preserving the original domain for routing; the router's
final DNS answer remains part of the trusted local configuration.
