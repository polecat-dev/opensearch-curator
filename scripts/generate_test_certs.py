#!/usr/bin/env python3
"""Generate TLS assets for the docker-compose.test.yml stack.

The script creates a password-protected root CA plus separate HTTP and transport
certificates (each with its own encrypted private key, full-chain bundle, and a
PKCS#12 keystore for the HTTP endpoint). All artefacts are stored under
``certs/generated/`` and are ignored by git.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "certs" / "generated"
DEFAULT_PASSWORD = "curatorssl"
DEFAULT_DAYS = 3650
DEFAULT_HTTP_CN = "opensearch-http.local"
DEFAULT_TRANSPORT_CN = "opensearch-transport.local"
DEFAULT_SAN_DNS = [
    "localhost",
    "opensearch",
    "opensearch-test",
    "opensearch-test-node",
]
DEFAULT_SAN_IP = [
    "127.0.0.1",
]


@dataclass
class CertificatePaths:
    base: Path
    ca_dir: Path
    http_dir: Path
    transport_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate self-signed CA, HTTP, and transport certificates for OpenSearch tests.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory for generated certificates.",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=DEFAULT_PASSWORD,
        help="Password that protects every generated private key and PKCS#12 bundle.",
    )
    parser.add_argument(
        "--openssl",
        dest="openssl_binary",
        default="openssl",
        help="Path to the openssl executable.",
    )
    parser.add_argument(
        "--http-cn",
        default=DEFAULT_HTTP_CN,
        help="Common Name used for the HTTP certificate subject.",
    )
    parser.add_argument(
        "--transport-cn",
        default=DEFAULT_TRANSPORT_CN,
        help="Common Name used for the transport certificate subject.",
    )
    parser.add_argument(
        "--ca-cn",
        default="OpenSearch Curator Dev CA",
        help="Common Name for the generated root CA.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help="Validity period (in days) for every certificate.",
    )
    parser.add_argument(
        "--extra-dns",
        action="append",
        default=[],
        dest="extra_dns",
        help="Additional DNS Subject Alternative Names (applied to both HTTP and transport certs).",
    )
    parser.add_argument(
        "--extra-ip",
        action="append",
        default=[],
        dest="extra_ip",
        help="Additional IP Subject Alternative Names (applied to both HTTP and transport certs).",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite any existing certificates instead of aborting.",
    )
    return parser.parse_args()


def resolve_openssl(binary: str) -> str:
    candidate = Path(binary)
    if candidate.exists():
        return str(candidate)
    located = shutil.which(binary)
    if located:
        return located
    raise FileNotFoundError(f"Unable to find openssl executable '{binary}'.")


def run_openssl(binary: str, args: List[str]) -> None:
    cmd = [binary] + args
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        sys.stderr.write("\n".join(["Failed command:", " ".join(cmd), result.stderr]))
        raise RuntimeError(f"openssl command failed with exit code {result.returncode}")


def info(message: str) -> None:
    print(f"[ssl] {message}")


def prepare_directories(base: Path, force: bool) -> CertificatePaths:
    base.mkdir(parents=True, exist_ok=True)
    ca_dir = base / "ca"
    http_dir = base / "http"
    transport_dir = base / "transport"
    for path in (ca_dir, http_dir, transport_dir):
        if path.exists():
            if force:
                shutil.rmtree(path)
            elif any(path.iterdir()):
                raise SystemExit(
                    f"{path} already contains files. "
                    "Use --force to delete them or choose another output directory."
                )
        path.mkdir(parents=True, exist_ok=True)
    return CertificatePaths(base=base, ca_dir=ca_dir, http_dir=http_dir, transport_dir=transport_dir)


def write_ext_file(target: Path, cn: str, dns_entries: Iterable[str], ip_entries: Iterable[str]) -> Path:
    dns_names = []
    for candidate in (cn, *dns_entries):
        if candidate not in dns_names:
            dns_names.append(candidate)
    content: List[str] = [
        "[v3_req]",
        "subjectAltName = @alt_names",
        "",
        "[alt_names]",
    ]
    for idx, name in enumerate(dns_names, 1):
        content.append(f"DNS.{idx} = {name}")
    for idx, ip in enumerate(ip_entries, 1):
        content.append(f"IP.{idx} = {ip}")
    target.write_text("\n".join(content), encoding="utf-8")
    return target


def generate_ca(
    openssl_bin: str,
    paths: CertificatePaths,
    password: str,
    ca_cn: str,
    days: int,
) -> tuple[Path, Path]:
    key_path = paths.ca_dir / "root-ca.key"
    cert_path = paths.ca_dir / "root-ca.pem"
    info("Generating encrypted root CA private key...")
    run_openssl(
        openssl_bin,
        [
            "genrsa",
            "-aes256",
            "-passout",
            f"pass:{password}",
            "-out",
            str(key_path),
            "4096",
        ],
    )
    info("Creating self-signed root CA certificate...")
    subject = f"/C=US/ST=Test/L=Curator/O=OpenSearch/OU=Dev/CN={ca_cn}"
    run_openssl(
        openssl_bin,
        [
            "req",
            "-x509",
            "-new",
            "-key",
            str(key_path),
            "-sha256",
            "-days",
            str(days),
            "-subj",
            subject,
            "-out",
            str(cert_path),
            "-passin",
            f"pass:{password}",
        ],
    )
    return key_path, cert_path


def generate_certificate(
    openssl_bin: str,
    ca_key: Path,
    ca_cert: Path,
    password: str,
    days: int,
    cn: str,
    output_dir: Path,
    dns_san: Iterable[str],
    ip_san: Iterable[str],
) -> dict:
    key_path = output_dir / f"{cn}.key"
    csr_path = output_dir / f"{cn}.csr"
    cert_path = output_dir / f"{cn}.crt"
    fullchain_path = output_dir / f"{cn}-fullchain.pem"
    ext_path = output_dir / f"{cn}.ext"
    info(f"Generating encrypted private key for {cn}...")
    run_openssl(
        openssl_bin,
        [
            "genrsa",
            "-aes256",
            "-passout",
            f"pass:{password}",
            "-out",
            str(key_path),
            "4096",
        ],
    )
    info(f"Creating CSR for {cn}...")
    subject = f"/C=US/ST=Test/L=Curator/O=OpenSearch/OU=Dev/CN={cn}"
    run_openssl(
        openssl_bin,
        [
            "req",
            "-new",
            "-key",
            str(key_path),
            "-out",
            str(csr_path),
            "-subj",
            subject,
            "-passin",
            f"pass:{password}",
        ],
    )
    write_ext_file(ext_path, cn, dns_san, ip_san)
    info(f"Signing certificate for {cn}...")
    serial_file = ca_cert.with_suffix(".srl")
    run_openssl(
        openssl_bin,
        [
            "x509",
            "-req",
            "-in",
            str(csr_path),
            "-CA",
            str(ca_cert),
            "-CAkey",
            str(ca_key),
            "-CAcreateserial",
            "-CAserial",
            str(serial_file),
            "-out",
            str(cert_path),
            "-days",
            str(days),
            "-sha256",
            "-extensions",
            "v3_req",
            "-extfile",
            str(ext_path),
            "-passin",
            f"pass:{password}",
        ],
    )
    with cert_path.open("r", encoding="utf-8") as leaf, ca_cert.open("r", encoding="utf-8") as ca_src:
        fullchain_path.write_text(leaf.read() + ca_src.read(), encoding="utf-8")
    for tmp in (csr_path, ext_path):
        if tmp.exists():
            tmp.unlink()
    return {
        "key": key_path,
        "cert": cert_path,
        "fullchain": fullchain_path,
    }


def create_pkcs12_bundle(
    openssl_bin: str,
    cert: Path,
    key: Path,
    ca_cert: Path,
    password: str,
    alias: str,
    target: Path,
) -> None:
    info(f"Creating PKCS#12 keystore ({target.name})...")
    run_openssl(
        openssl_bin,
        [
            "pkcs12",
            "-export",
            "-out",
            str(target),
            "-name",
            alias,
            "-inkey",
            str(key),
            "-in",
            str(cert),
            "-certfile",
            str(ca_cert),
            "-passin",
            f"pass:{password}",
            "-passout",
            f"pass:{password}",
        ],
    )


def write_manifest(paths: CertificatePaths, password: str, manifest: dict) -> None:
    manifest_path = paths.base / "manifest.json"
    manifest_data = {
        "password_env": "OPENSEARCH_TEST_SSL_PASSWORD",
        "password": password,
        "artifacts": manifest,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    password_env = paths.base / "passwords.env"
    password_env.write_text(
        dedent(
            f"""\
            # Values consumed by docker-compose.test.yml
            OPENSEARCH_TEST_SSL_PASSWORD={password}
            TEST_ES_CA_CERT={paths.ca_dir / "root-ca.pem"}
            TEST_ES_SERVER=https://localhost:19200
            """
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    try:
        openssl_bin = resolve_openssl(args.openssl_binary)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    paths = prepare_directories(args.output, args.force)
    dns_entries = DEFAULT_SAN_DNS + args.extra_dns
    ip_entries = DEFAULT_SAN_IP + args.extra_ip

    ca_key, ca_cert = generate_ca(openssl_bin, paths, args.password, args.ca_cn, args.days)

    transport = generate_certificate(
        openssl_bin,
        ca_key,
        ca_cert,
        args.password,
        args.days,
        args.transport_cn,
        paths.transport_dir,
        dns_entries,
        ip_entries,
    )

    http = generate_certificate(
        openssl_bin,
        ca_key,
        ca_cert,
        args.password,
        args.days,
        args.http_cn,
        paths.http_dir,
        dns_entries,
        ip_entries,
    )

    pkcs12_path = paths.http_dir / "opensearch-http.p12"
    create_pkcs12_bundle(
        openssl_bin,
        cert=http["cert"],
        key=http["key"],
        ca_cert=ca_cert,
        password=args.password,
        alias="opensearch-http",
        target=pkcs12_path,
    )

    manifest = {
        "ca": {
            "key": str(ca_key),
            "cert": str(ca_cert),
        },
        "http": {
            "key": str(http["key"]),
            "cert": str(http["cert"]),
            "fullchain": str(http["fullchain"]),
            "pkcs12": str(pkcs12_path),
        },
        "transport": {
            "key": str(transport["key"]),
            "cert": str(transport["cert"]),
            "fullchain": str(transport["fullchain"]),
        },
    }
    write_manifest(paths, args.password, manifest)

    info("All certificates generated successfully.")
    info(f"Root CA: {ca_cert}")
    info(f"HTTP cert: {http['cert']}")
    info(f"Transport cert: {transport['cert']}")
    info("Remember to update your .env file with TEST_ES_SERVER, TEST_ES_CA_CERT, "
         "and OPENSEARCH_TEST_SSL_PASSWORD before running docker-compose.")


if __name__ == "__main__":
    main()
