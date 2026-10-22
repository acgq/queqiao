# Fork extensions

This file describes local extensions without changing upstream documentation.

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
