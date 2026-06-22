#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # If starting the development server without a port, append default from settings
    if 'runserver' in sys.argv and not any(arg for arg in sys.argv[1:] if ':' in arg or arg.isdigit()):
        try:
            from django.conf import settings
            port = getattr(settings, 'DJANGO_PORT', 8000)
            # If port is 0, pick a free ephemeral port
            if int(port) == 0:
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    port = s.getsockname()[1]
            sys.argv += [f'0.0.0.0:{port}']
        except Exception:
            # Fallback to default Django port
            sys.argv += ['8000']

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
