"""Append-only transcript + TranscriptHash helpers."""

import os
import hashlib
from typing import List, Optional
from datetime import datetime


class Transcript:
    """Append-only transcript for session messages."""
    
    def __init__(self, transcript_file: str):
        """
        Initialize transcript.
        
        Args:
            transcript_file: Path to transcript file
        """
        self.transcript_file = transcript_file
        self.entries: List[str] = []
        self.first_seq: Optional[int] = None
        self.last_seq: Optional[int] = None
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(transcript_file) if os.path.dirname(transcript_file) else '.', exist_ok=True)
        
        # Load existing transcript if it exists
        if os.path.exists(transcript_file):
            self._load_transcript()
    
    def _load_transcript(self):
        """Load existing transcript from file."""
        try:
            with open(self.transcript_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.entries.append(line)
                        # Extract sequence number from line
                        parts = line.split('|')
                        if len(parts) > 0:
                            try:
                                seqno = int(parts[0])
                                if self.first_seq is None:
                                    self.first_seq = seqno
                                self.last_seq = seqno
                            except ValueError:
                                pass
        except Exception as e:
            print(f"Error loading transcript: {e}")
    
    def append_message(self, seqno: int, timestamp: int, ciphertext: str, signature: str, peer_cert_fingerprint: str):
        """
        Append a message to the transcript.
        
        Args:
            seqno: Sequence number
            timestamp: Timestamp in milliseconds
            ciphertext: Base64 encoded ciphertext
            signature: Base64 encoded signature
            peer_cert_fingerprint: Peer certificate fingerprint
        """
        # Format: seqno | timestamp | ciphertext | signature | peer_cert_fingerprint
        entry = f"{seqno}|{timestamp}|{ciphertext}|{signature}|{peer_cert_fingerprint}"
        self.entries.append(entry)
        
        # Update sequence number range
        if self.first_seq is None:
            self.first_seq = seqno
        self.last_seq = seqno
        
        # Append to file (append-only)
        with open(self.transcript_file, 'a') as f:
            f.write(entry + '\n')
    
    def compute_transcript_hash(self) -> str:
        """
        Compute SHA-256 hash of the transcript.
        
        TranscriptHash = SHA256(concatenation of all transcript lines)
        
        Returns:
            Hexadecimal SHA-256 hash of the transcript
        """
        # Concatenate all transcript entries
        transcript_content = '\n'.join(self.entries)
        
        # Compute SHA-256 hash
        hash_value = hashlib.sha256(transcript_content.encode('utf-8')).digest()
        
        # Return as hexadecimal string
        return hash_value.hex()
    
    def get_first_seq(self) -> Optional[int]:
        """Get first sequence number."""
        return self.first_seq
    
    def get_last_seq(self) -> Optional[int]:
        """Get last sequence number."""
        return self.last_seq
    
    def get_entries(self) -> List[str]:
        """Get all transcript entries."""
        return self.entries.copy()
    
    def clear(self):
        """Clear transcript (for testing purposes)."""
        self.entries = []
        self.first_seq = None
        self.last_seq = None
        if os.path.exists(self.transcript_file):
            os.remove(self.transcript_file)


def verify_transcript(transcript_file: str, expected_hash: str) -> bool:
    """
    Verify transcript hash.
    
    Args:
        transcript_file: Path to transcript file
        expected_hash: Expected SHA-256 hash
    
    Returns:
        True if hash matches, False otherwise
    """
    try:
        transcript = Transcript(transcript_file)
        computed_hash = transcript.compute_transcript_hash()
        return computed_hash.lower() == expected_hash.lower()
    except Exception as e:
        print(f"Error verifying transcript: {e}")
        return False
