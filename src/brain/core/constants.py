# Core Constitutional Constants

"""
Immutable constitutional metadata shared across the Hermes cognitive pipeline.

These values are architecture-frozen (B.8) and must not be redefined at
engine level. Engines and pipeline orchestrators import from here so a
single authoritative source exists for constitutional identity.
"""

CONSTITUTIONAL_VERSION: str = "1.0.0"
CONSTITUTIONAL_SPEC_NAME: str = "B.8"
