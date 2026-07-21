# Desktop App Auth Provider

Inline `DashboardAuthProvider` that lets the Hermes Desktop app authenticate with a token instead of Nous OAuth.

## When to Use

- You run `hermes dashboard --host 0.0.0.0` (public bind, auth gate engaged)
- `/api/status` returns `auth_providers: ["nous"]` → desktop shows "Sign in with Nous"
- You want username/password login with a static token from `.env`

## Full Provider Class

Add to `web_server.py` at the top of `_lifespan()`, right after the `async def _lifespan(app)` line:

```python
@asynccontextmanager
async def _lifespan(app: "FastAPI"):
    # Register a password auth provider that accepts the session token
    from hermes_cli.dashboard_auth import register_provider
    from hermes_cli.dashboard_auth.base import (
        DashboardAuthProvider,
        InvalidCredentialsError,
        Session,
    )
    import hmac, os, time

    class _TokenPasswordProvider(DashboardAuthProvider):
        name = "password"
        display_name = "Access Token"
        supports_password = True
        supports_token = True

        def start_login(self, *, redirect_uri):
            raise NotImplementedError
        def complete_login(self, *, code, state, code_verifier, redirect_uri):
            raise NotImplementedError

        def complete_password_login(self, *, username, password):
            token = os.environ.get("HERMES_DASHBOARD_SESSION_TOKEN", "")
            if not token:
                from hermes_cli.web_server import _SESSION_TOKEN
                token = _SESSION_TOKEN or ""
            if hmac.compare_digest(username, token) or hmac.compare_digest(password, token):
                return Session(
                    user_id="token-user", email="token@local",
                    display_name="Token User", org_id="", provider="password",
                    expires_at=int(time.time()) + 86400,
                    access_token=token, refresh_token=token,
                )
            raise InvalidCredentialsError()

        def verify_session(self, *, access_token):
            from hermes_cli.web_server import _SESSION_TOKEN
            expected = _SESSION_TOKEN or ""
            if hmac.compare_digest(access_token, expected):
                return Session(
                    user_id="token-user", email="token@local",
                    display_name="Token User", org_id="", provider="password",
                    expires_at=int(time.time()) + 86400,
                    access_token=expected, refresh_token=expected,
                )
            return None

        def refresh_session(self, *, refresh_token):
            try:
                return self.complete_password_login(
                    username=refresh_token, password=refresh_token
                )
            except InvalidCredentialsError:
                raise RefreshExpiredError()

        def revoke_session(self, *, refresh_token):
            pass

    register_provider(_TokenPasswordProvider())
```

## How Login Works

1. Desktop app calls `GET /api/status` → sees `["nous", "password"]`
2. Renders a username/password form (because `supports_password=True` provider exists)
3. User enters the session token as both username and password
4. Desktop POSTs `{"provider":"password","username":"<token>","password":"<token>"}` to `/auth/password-login`
5. Server returns `{"ok":true,"next":"/"}` with session cookies
6. Desktop connects WS with `?token=<token>` (requires the [WS token patch](../references/websocket-auth.md))
7. REST calls use `Authorization: Bearer <token>` header

## Token Source

Set in `~/.hermes/.env`:
```
HERMES_DASHBOARD_SESSION_TOKEN=test-token-hermes-mobile-2026
```

python-dotenv uses the **last** value if duplicated.
