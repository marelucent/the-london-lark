import unittest
import werkzeug

# Compatibility for Werkzeug 3.x where __version__ is removed
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3"

import app


class APIMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()

    def test_api_venues_includes_summary(self):
        response = self.client.get('/api/venues')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('venues', data)
        self.assertTrue(data['venues'])

        summary = data.get('summary', {})
        self.assertIn('counts', summary)
        self.assertEqual(summary['counts'].get('venues'), len(data['venues']))
        self.assertIn('tags', summary)
        self.assertIn('moods', summary['tags'])
        self.assertIn('genres', summary['tags'])

    def test_api_summary_has_verification_details(self):
        response = self.client.get('/api/venues/summary')
        self.assertEqual(response.status_code, 200)

        summary = response.get_json()
        verification = summary.get('verification', {})

        self.assertIn('verified', verification)
        self.assertIn('missing', verification)
        self.assertIn('missing_names', verification)
        self.assertIn('recently_verified', verification)


if __name__ == '__main__':
    unittest.main()
