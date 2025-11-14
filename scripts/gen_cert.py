"""Issue server/client cert signed by Root CA (SAN=DNSName(CN))."""

import argparse
import os
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta


def generate_certificate(
    cn: str,
    output_prefix: str,
    ca_cert_path: str = "certs/ca_cert.pem",
    ca_key_path: str = "certs/ca_key.pem",
    key_size: int = 2048,
    validity_days: int = 365,
    is_server: bool = False
):
    """
    Generate a certificate signed by the Root CA.
    
    Args:
        cn: Common Name (CN) for the certificate
        output_prefix: Output file prefix (e.g., "server" or "client")
        ca_cert_path: Path to CA certificate
        ca_key_path: Path to CA private key
        key_size: RSA key size in bits
        validity_days: Certificate validity period in days
        is_server: True for server certificate, False for client certificate
    """
    # Create output directory
    certs_dir = "certs"
    os.makedirs(certs_dir, exist_ok=True)
    
    # Load CA certificate and private key
    print(f"Loading CA certificate from: {ca_cert_path}")
    with open(ca_cert_path, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    
    print(f"Loading CA private key from: {ca_key_path}")
    with open(ca_key_path, "rb") as f:
        ca_key = load_pem_private_key(f.read(), password=None, backend=default_backend())
    
    # Generate RSA private key for the certificate
    print(f"Generating RSA-{key_size} private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    # Create certificate subject
    print(f"Creating certificate: {cn}")
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PK"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Pakistan"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Karachi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FAST-NUCES"),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])
    
    # Build certificate
    cert_builder = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=validity_days)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(cn),
        ]),
        critical=False,
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    
    # Add appropriate key usage based on certificate type
    if is_server:
        cert_builder = cert_builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    else:
        cert_builder = cert_builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    
    # Sign certificate with CA private key
    cert = cert_builder.sign(ca_key, hashes.SHA256())
    
    # Save private key
    key_path = os.path.join(certs_dir, f"{output_prefix}_key.pem")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ))
    print(f"Private key saved to: {key_path}")
    
    # Save certificate
    cert_path = os.path.join(certs_dir, f"{output_prefix}_cert.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(Encoding.PEM))
    print(f"Certificate saved to: {cert_path}")
    
    # Display certificate information
    print("\nCertificate Information:")
    print(f"  Subject: {cert.subject}")
    print(f"  Issuer: {cert.issuer}")
    print(f"  Serial Number: {cert.serial_number}")
    print(f"  Valid From: {cert.not_valid_before}")
    print(f"  Valid To: {cert.not_valid_after}")
    print(f"  Fingerprint (SHA-256): {cert.fingerprint(hashes.SHA256()).hex()}")


def main():
    parser = argparse.ArgumentParser(description="Generate certificate signed by Root CA")
    parser.add_argument("--cn", required=True, help="Common Name (CN) for the certificate")
    parser.add_argument("--out", required=True, help="Output file prefix (e.g., 'server' or 'client')")
    parser.add_argument("--ca-cert", default="certs/ca_cert.pem", help="Path to CA certificate")
    parser.add_argument("--ca-key", default="certs/ca_key.pem", help="Path to CA private key")
    parser.add_argument("--key-size", type=int, default=2048, help="RSA key size in bits (default: 2048)")
    parser.add_argument("--validity-days", type=int, default=365, help="Certificate validity period in days (default: 365)")
    parser.add_argument("--server", action="store_true", help="Generate server certificate (default: client certificate)")
    
    args = parser.parse_args()
    
    try:
        generate_certificate(
            args.cn,
            args.out,
            args.ca_cert,
            args.ca_key,
            args.key_size,
            args.validity_days,
            args.server
        )
        print("\nCertificate generation completed successfully!")
    except Exception as e:
        print(f"\nError generating certificate: {e}")
        raise


if __name__ == "__main__":
    main()
