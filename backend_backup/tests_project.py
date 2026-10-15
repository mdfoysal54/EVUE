from django.test import SimpleTestCase, override_settings
from django.conf import settings

class ProjectConfigurationTests(SimpleTestCase):
    def test_domain_apps_installed(self):
        for name in ("catalog", "accounts", "operations", "commerce"):
            self.assertIn(name, settings.INSTALLED_APPS)

    def test_csrf_middleware_present(self):
        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)

    def test_authentication_middleware_present(self):
        self.assertIn("django.contrib.auth.middleware.AuthenticationMiddleware", settings.MIDDLEWARE)
