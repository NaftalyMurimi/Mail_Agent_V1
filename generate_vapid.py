from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import base64

private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key  = private_key.public_key()

pub_bytes = public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

priv_b64 = base64.urlsafe_b64encode(
    private_key.private_numbers().private_value.to_bytes(32, 'big')
).rstrip(b'=').decode()

pub_b64 = base64.urlsafe_b64encode(pub_bytes).rstrip(b'=').decode()

print('Copy these into your .env files:')
print()
print(f'VAPID_PRIVATE_KEY={priv_b64}')
print(f'VAPID_PUBLIC_KEY={pub_b64}')