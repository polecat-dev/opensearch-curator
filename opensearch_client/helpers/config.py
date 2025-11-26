"""Deprecated helper shim for opensearch_client.config."""

# pylint: disable=wildcard-import,unused-wildcard-import
import warnings

from ..config import *  # noqa: F401,F403

warnings.warn(
    (
        "es_client.helpers.config is deprecated. Use es_client.config instead. "
        "This shim will be removed in 9.0.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)
