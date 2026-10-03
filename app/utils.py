import secrets
import string


def generate_pickup_token(prefix: str = "LIB") -> str:
    """Generate a clean, human-readable unique pick-up token.
    
    Example output: LIB-A8K2-9M4P
    """
    chars = string.ascii_uppercase + string.digits
    # Exclude ambiguous characters if needed, but standard uppercase+digits is very standard
    part1 = ''.join(secrets.choice(chars) for _ in range(4))
    part2 = ''.join(secrets.choice(chars) for _ in range(4))
    return f"{prefix}-{part1}-{part2}"
