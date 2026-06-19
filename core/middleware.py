from django.utils.deprecation import MiddlewareMixin
from django.db import connection


class AuditMiddleware(MiddlewareMixin):
    """Set a session-level DB setting with the current user id so DB triggers
    can attribute changes even for direct DB edits when requests go through Django.

    The middleware sets app.audit_user to the user PK (or 'anonymous') at
    request start and clears it on response. Uses set_config so triggers can
    read current_setting('app.audit_user', true).
    """

    def process_request(self, request):
        try:
            user = getattr(request, "user", None)
            user_id = str(user.pk) if user and getattr(user, "is_authenticated", False) else "anonymous"
            with connection.cursor() as curs:
                # store per-session value; cleared at end of response
                curs.execute("SELECT set_config('app.audit_user', %s, false)", [user_id])
        except Exception:
            # Don't break requests if DB is unavailable here
            pass

    def process_response(self, request, response):
        try:
            with connection.cursor() as curs:
                curs.execute("SELECT set_config('app.audit_user', '', false)")
        except Exception:
            pass
        return response
