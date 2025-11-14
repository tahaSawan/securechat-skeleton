#!/usr/bin/env python3
"""Offline verification of transcript and session receipt."""

import sys
import os
import json
import glob
import argparse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.storage.transcript import Transcript
from app.crypto.sign import verify_signature, load_public_key_from_cert
from app.crypto.pki import load_certificate_from_file, get_cert_fingerprint
from app.common.utils import b64d

load_dotenv()


def verify_transcript(transcript_file: str):
    """Verify transcript integrity."""
    print("=" * 60)
    print("Transcript Verification")
    print("=" * 60)
    
    if not os.path.exists(transcript_file):
        print(f"❌ ERROR: Transcript file not found: {transcript_file}")
        return False
    
    print(f"\n1. Loading transcript: {transcript_file}")
    transcript = Transcript(transcript_file)
    
    # Compute transcript hash
    transcript_hash = transcript.compute_transcript_hash()
    print(f"   ✓ Transcript hash: {transcript_hash}")
    print(f"   ✓ Hash length: {len(transcript_hash)} characters")
    
    # Display transcript entries
    entries = transcript.get_entries()
    print(f"\n2. Transcript entries: {len(entries)}")
    for i, entry in enumerate(entries, 1):
        parts = entry.split('|')
        if len(parts) >= 5:
            seqno = parts[0]
            timestamp = parts[1]
            ciphertext = parts[2][:20] + "..." if len(parts[2]) > 20 else parts[2]
            signature = parts[3][:20] + "..." if len(parts[3]) > 20 else parts[3]
            fingerprint = parts[4]
            
            print(f"   Entry {i}:")
            print(f"      seqno: {seqno}")
            print(f"      timestamp: {timestamp}")
            print(f"      ciphertext: {ciphertext}")
            print(f"      signature: {signature}")
            print(f"      peer_cert_fingerprint: {fingerprint}")
    
    # Verify sequence numbers
    print(f"\n3. Verifying sequence numbers...")
    first_seq = transcript.get_first_seq()
    last_seq = transcript.get_last_seq()
    print(f"   ✓ First seqno: {first_seq}")
    print(f"   ✓ Last seqno: {last_seq}")
    
    # Verify sequence numbers are increasing
    seqnos = []
    for entry in entries:
        parts = entry.split('|')
        if len(parts) >= 1:
            seqno = int(parts[0])
            seqnos.append(seqno)
    
    is_increasing = all(seqnos[i] < seqnos[i+1] for i in range(len(seqnos)-1))
    if is_increasing:
        print(f"   ✅ Sequence numbers are strictly increasing")
    else:
        print(f"   ❌ Sequence numbers are not strictly increasing")
        return False
    
    print(f"\n✅ Transcript verification passed!")
    return transcript_hash


def verify_receipt(receipt_file: str, transcript_hash: str, cert_path: str):
    """Verify session receipt signature."""
    print("\n" + "=" * 60)
    print("Session Receipt Verification")
    print("=" * 60)
    
    if not os.path.exists(receipt_file):
        print(f"⚠️  Receipt file not found: {receipt_file}")
        print("   Creating receipt from transcript...")
        return False
    
    print(f"\n1. Loading receipt: {receipt_file}")
    with open(receipt_file, 'r') as f:
        receipt = json.load(f)
    
    print(f"   ✓ Receipt type: {receipt.get('type')}")
    print(f"   ✓ Peer: {receipt.get('peer')}")
    print(f"   ✓ First seq: {receipt.get('first_seq')}")
    print(f"   ✓ Last seq: {receipt.get('last_seq')}")
    print(f"   ✓ Transcript hash: {receipt.get('transcript_sha256')}")
    
    # Verify transcript hash matches
    receipt_hash = receipt.get('transcript_sha256', '')
    if receipt_hash == transcript_hash:
        print(f"\n2. Transcript hash matches receipt hash ✅")
    else:
        print(f"\n2. Transcript hash does not match receipt hash ❌")
        print(f"   Transcript hash: {transcript_hash}")
        print(f"   Receipt hash: {receipt_hash}")
        return False
    
    # Load certificate
    if not os.path.exists(cert_path):
        print(f"❌ ERROR: Certificate file not found: {cert_path}")
        return False
    
    print(f"\n3. Loading certificate: {cert_path}")
    cert = load_certificate_from_file(cert_path)
    public_key = load_public_key_from_cert(cert)
    
    # Get certificate fingerprint
    fingerprint = get_cert_fingerprint(cert)
    print(f"   ✓ Certificate fingerprint: {fingerprint}")
    
    # Verify signature
    print(f"\n4. Verifying receipt signature...")
    signature = receipt.get('sig', '')
    hash_bytes = bytes.fromhex(receipt_hash)
    signature_bytes = b64d(signature)
    
    is_valid = verify_signature(hash_bytes, signature_bytes, public_key)
    
    if is_valid:
        print(f"   ✅ Receipt signature is valid!")
    else:
        print(f"   ❌ Receipt signature is invalid!")
        return False
    
    print(f"\n✅ Receipt verification passed!")
    return True


def verify_message_signature(transcript_file: str, cert_path: str):
    """Verify each message signature in transcript."""
    print("\n" + "=" * 60)
    print("Message Signature Verification")
    print("=" * 60)
    
    if not os.path.exists(transcript_file):
        print(f"❌ ERROR: Transcript file not found: {transcript_file}")
        return False
    
    if not os.path.exists(cert_path):
        print(f"❌ ERROR: Certificate file not found: {cert_path}")
        return False
    
    print(f"\n1. Loading transcript: {transcript_file}")
    transcript = Transcript(transcript_file)
    
    print(f"\n2. Loading certificate: {cert_path}")
    cert = load_certificate_from_file(cert_path)
    public_key = load_public_key_from_cert(cert)
    
    # Verify each message
    entries = transcript.get_entries()
    print(f"\n3. Verifying {len(entries)} message(s)...")
    
    all_valid = True
    for i, entry in enumerate(entries, 1):
        parts = entry.split('|')
        if len(parts) >= 5:
            seqno = int(parts[0])
            timestamp = int(parts[1])
            ciphertext = parts[2]
            signature = parts[3]
            
            # Reconstruct hash data
            seqno_bytes = seqno.to_bytes(8, byteorder='big')
            ts_bytes = timestamp.to_bytes(8, byteorder='big')
            ct_bytes = b64d(ciphertext)
            hash_data = seqno_bytes + ts_bytes + ct_bytes
            
            # Verify signature
            sig_bytes = b64d(signature)
            is_valid = verify_signature(hash_data, sig_bytes, public_key)
            
            if is_valid:
                print(f"   Entry {i} (seqno={seqno}): ✅ Valid signature")
            else:
                print(f"   Entry {i} (seqno={seqno}): ❌ Invalid signature")
                all_valid = False
    
    if all_valid:
        print(f"\n✅ All message signatures are valid!")
    else:
        print(f"\n❌ Some message signatures are invalid!")
    
    return all_valid


def test_transcript_modification(transcript_file: str):
    """Test that transcript modification breaks verification."""
    print("\n" + "=" * 60)
    print("Transcript Modification Test")
    print("=" * 60)
    
    if not os.path.exists(transcript_file):
        print(f"❌ ERROR: Transcript file not found: {transcript_file}")
        return False
    
    print(f"\n1. Loading original transcript: {transcript_file}")
    transcript = Transcript(transcript_file)
    original_hash = transcript.compute_transcript_hash()
    print(f"   ✓ Original hash: {original_hash}")
    
    # Modify transcript
    print(f"\n2. Modifying transcript...")
    modified_transcript = Transcript(transcript_file)
    modified_transcript.entries.append("999|9999999999999|fake_ciphertext|fake_signature|fake_fingerprint")
    modified_hash = modified_transcript.compute_transcript_hash()
    print(f"   ✓ Modified hash: {modified_hash}")
    
    # Verify hash changed
    if original_hash != modified_hash:
        print(f"\n3. ✅ Hash changed after modification")
        print(f"   Original: {original_hash[:32]}...")
        print(f"   Modified: {modified_hash[:32]}...")
        print(f"   ✓ Any edit breaks verification")
        return True
    else:
        print(f"\n3. ❌ Hash did not change after modification")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify transcript and session receipt")
    parser.add_argument("--transcript", type=str, help="Transcript file path")
    parser.add_argument("--receipt", type=str, help="Receipt file path (JSON)")
    parser.add_argument("--cert", type=str, help="Certificate file path")
    parser.add_argument("--verify-messages", action="store_true", help="Verify each message signature")
    parser.add_argument("--test-modification", action="store_true", help="Test transcript modification")
    
    args = parser.parse_args()
    
    # If no transcript specified, find the most recent one
    if not args.transcript:
        transcript_dir = os.getenv("TRANSCRIPT_DIR", "transcripts")
        transcripts = glob.glob(f"{transcript_dir}/client_*.txt")
        if transcripts:
            args.transcript = max(transcripts, key=os.path.getctime)
            print(f"Using most recent transcript: {args.transcript}")
        else:
            print("❌ ERROR: No transcript file found")
            print("   Run the system first to generate transcripts")
            return 1
    
    # Verify transcript
    transcript_hash = verify_transcript(args.transcript)
    if not transcript_hash:
        return 1
    
    # Verify receipt if provided
    if args.receipt and args.cert:
        if not verify_receipt(args.receipt, transcript_hash, args.cert):
            return 1
    
    # Verify message signatures if requested
    if args.verify_messages:
        if not args.cert:
            print("❌ ERROR: Certificate file required for message signature verification")
            return 1
        if not verify_message_signature(args.transcript, args.cert):
            return 1
    
    # Test transcript modification if requested
    if args.test_modification:
        if not test_transcript_modification(args.transcript):
            return 1
    
    print("\n" + "=" * 60)
    print("All verifications passed! ✅")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

