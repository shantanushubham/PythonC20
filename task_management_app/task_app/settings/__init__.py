"""
Environment-specific settings loaded via APP_ENV.

  APP_ENV=local  (default) — your machine
  APP_ENV=dev              — shared dev / E2E server
  APP_ENV=prod             — production
"""

import os

_env = os.environ.get("APP_ENV", "local").lower()

if _env == "prod":
    from .prod import *  # noqa: F403
elif _env == "dev":
    from .dev import *  # noqa: F403
else:
    from .local import *  # noqa: F403
