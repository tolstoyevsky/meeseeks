"""Module contains tests for HappyBirthder application. """

import os
from unittest import mock

os.environ.setdefault('GIPHY_API_KEY', 'dummy-giphy-key')

# Imports after the os.environ call are intentional: settings reads GIPHY_API_KEY
# at import time, so the dummy key must be set first.
# pylint: disable=wrong-import-position

from aiohttp import ClientResponseError

from apps.happy_birthder import happy_birthder, settings
from apps.happy_birthder.happy_birthder import GifReceiver
from tests.base import BaseTestClass


class MockResponse:
    """Simple async response mock for aiohttp. """

    def __init__(self, json_data=None, exc=None):
        self._json_data = json_data
        self._exc = exc

    async def json(self):
        """Return mocked JSON body. """

        if self._exc:
            raise self._exc
        return self._json_data

    async def __aenter__(self):
        """Enter async context. """

        return self

    async def __aexit__(self, *args):
        """Exit async context. """

        return False

    @property
    def raises(self):
        """Return whether the response should simulate an HTTP error. """

        return self._exc is not None

    @property
    def exc(self):
        """Return the exception to raise. """

        return self._exc


class MockSession:
    """Simple async session mock for aiohttp. """

    def __init__(self, response):
        self._response = response

    async def get(self, *_args, **_kwargs):
        """Return mocked response or raise simulated error. """

        if self._response.raises:
            raise self._response.exc

        return self._response

    async def __aenter__(self):
        """Enter async context. """

        return self

    async def __aexit__(self, *args):
        """Exit async context. """

        return False


class TestGifReceiver(BaseTestClass):
    """Tests of GifReceiver class. """

    def setUp(self):
        """Patching variables before run tests. """

        super().setUp()
        self._patches = [
            mock.patch.object(settings, 'GIPHY_API_URL', 'https://api.giphy.com/v1/', create=True),
            mock.patch.object(settings, 'GIPHY_IMAGE_LIMIT', 5, create=True),
            mock.patch.object(settings, 'GIPHY_RATING', 'g', create=True),
            mock.patch.object(settings, 'GIPHY_SEARCH_TERMS', ['test_tag'], create=True),
            mock.patch.object(settings, 'GIPHY_BLACKLISTED_GIF_IDS', [], create=True),
            mock.patch.object(settings, 'GIPHY_MAX_ATTEMPTS', 1, create=True),
        ]
        for patcher in self._patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    @staticmethod
    def _giphy_search_response(gif_ids):
        """Return a synthetic GIPHY search response for the given GIF IDs. """

        return {
            'data': [
                {
                    'id': gif_id,
                    'images': {
                        'original': {
                            'url': f'https://media.giphy.com/media/{gif_id}/giphy.gif',
                        },
                    },
                }
                for gif_id in gif_ids
            ],
        }

    @staticmethod
    def _patch_client_session(response):
        """Patch aiohttp ClientSession to return the given mock response. """

        return mock.patch.object(happy_birthder, 'ClientSession',
                                 return_value=MockSession(response))

    def test_get_random_gif_url_returns_url(self):
        """Test GifReceiver returns one of the GIF URLs from GIPHY response. """

        @self.async_case
        async def body():
            response = MockResponse(self._giphy_search_response(['gif1', 'gif2']))
            with self._patch_client_session(response):
                url = await GifReceiver('test-key').get_random_gif_url()

            self.assertIn(url, [
                'https://media.giphy.com/media/gif1/giphy.gif',
                'https://media.giphy.com/media/gif2/giphy.gif',
            ])

    def test_get_random_gif_url_excludes_blacklisted(self):
        """Test GifReceiver excludes blacklisted GIF IDs. """

        @self.async_case
        async def body():
            with mock.patch.object(settings, 'GIPHY_BLACKLISTED_GIF_IDS', ['gif1'], create=True):
                response = MockResponse(self._giphy_search_response(['gif1', 'gif2']))
                with self._patch_client_session(response):
                    url = await GifReceiver('test-key').get_random_gif_url()

            self.assertEqual(url, 'https://media.giphy.com/media/gif2/giphy.gif')

    def test_get_random_gif_url_returns_empty_on_http_error(self):
        """Test GifReceiver returns empty string on ClientResponseError. """

        @self.async_case
        async def body():
            response = MockResponse(exc=ClientResponseError(
                request_info=mock.Mock(),
                history=(),
                status=403,
            ))
            with self._patch_client_session(response):
                url = await GifReceiver('test-key').get_random_gif_url()

            self.assertEqual(url, '')

    def test_get_random_gif_url_returns_empty_when_no_results(self):
        """Test GifReceiver returns empty string when GIPHY returns no GIFs. """

        @self.async_case
        async def body():
            response = MockResponse({'data': []})
            with self.assertLogs('meeseeks-core', level='WARNING') as log_context:
                with self._patch_client_session(response):
                    url = await GifReceiver('test-key').get_random_gif_url()

            self.assertEqual(url, '')
            self.assertTrue(
                any('GIPHY returned no GIFs for tag' in message
                    for message in log_context.output)
            )
