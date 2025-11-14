"""Create Root CA (RSA + self-signed X.509) using cryptography."""

import argparse
import os
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta


def generate_ca(name: str = "FAST-NU Root CA", key_size: int = 2048, validity_days: int = 3650):
    """
    Generate a Root CA certificate and private key.
    
    Args:
        name: Common Name for the CA
        key_size: RSA key size in bits
        validity_days: Certificate validity period in days
    """
    # Create output directory
    certs_dir = "certs"
    os.makedirs(certs_dir, exist_ok=True)
    
    # Generate RSA private key
    print(f"Generating RSA-{key_size} private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    # Create self-signed certificate
    print(f"Creating self-signed CA certificate: {name}")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PK"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Pakistan"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Karachi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FAST-NUCES"),
        x509.NameAttribute(NameOID.COMMON_NAME, name),
    ])
    
    # Build certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            key_cert_sign=True,
            crl_sign=True,
            digital_signature=False,
            key_encipherment=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).sign(private_key, hashes.SHA256())
    
    # Save private key
    key_path = os.path.join(certs_dir, "ca_key.pem")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ))
    print(f"CA private key saved to: {key_path}")
    
    # Save certificate
    cert_path = os.path.join(certs_dir, "ca_cert.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(Encoding.PEM))
    print(f"CA certificate saved to: {cert_path}")
    
    # Display certificate information
    print("\nCA Certificate Information:")
    print(f"  Subject: {cert.subject}")
    print(f"  Issuer: {cert.issuer}")
    print(f"  Serial Number: {cert.serial_number}")
    print(f"  Valid From: {cert.not_valid_before}")
    print(f"  Valid To: {cert.not_valid_after}")
    print(f"  Fingerprint (SHA-256): {cert.fingerprint(hashes.SHA256()).hex()}")


def main():
    parser = argparse.ArgumentParser(description="Generate Root CA certificate and private key")
    parser.add_argument("--name", default="FAST-NU Root CA", help="Common Name for the CA")
    parser.add_argument("--key-size", type=int, default=2048, help="RSA key size in bits (default: 2048)")
    parser.add_argument("--validity-days", type=int, default=3650, help="Certificate validity period in days (default: 3650)")
    
    args = parser.parse_args()
    
    try:
        generate_ca(args.name, args.key_size, args.validity_days)
        print("\nCA generation completed successfully!")
    except Exception as e:
        print(f"\nError generating CA: {e}")
        raise


if __name__ == "__main__":
    main()
