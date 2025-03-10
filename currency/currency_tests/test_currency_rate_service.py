import datetime
from datetime import timezone

from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

from currency.models import Currency, CurrencyRateHistory
from currency.services import CurrencyRateService


@override_settings(APILAYER_API_KEYS=['81e7e9b0_fake_key'])
class TestCurrencyRateService(TestCase):
    def setUp(self) -> None:
        self.service = CurrencyRateService()

    @patch('currency.services.requests.get')
    def test_fetch_rates_live(self, mock_get: MagicMock) -> None:
        """
        We check that API_URL_LIVE is used if there is no date.
        """
        dummy_response = {
            "success": True,
            "terms": "https://currencylayer.com/terms",
            "privacy": "https://currencylayer.com/privacy",
            "timestamp": 1633017600,
            "source": "USD",
            "quotes": {"USDUSD": 1.0, "USDEUR": 0.85},
            "error": None,
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = dummy_response
        mock_get.return_value = mock_resp

        # Send None or today's date - wait for the live URL to be called.
        result1 = self.service.fetch_rates()
        self.assertEqual(result1, dummy_response)

        result2 = self.service.fetch_rates(date=datetime.date.today())
        self.assertEqual(result2, dummy_response)

        # Check that the live URL is used and the date parameter is missing
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.service.API_URL_LIVE)
        self.assertNotIn('date', kwargs['params'])

    @patch('currency.services.requests.get')
    def test_fetch_rates_historical(self, mock_get: MagicMock) -> None:
        """
        Check that API_URL_HISTORICAL is used when passing a date other than today's date.
        """
        dummy_response = {
            "success": True,
            "terms": "https://currencylayer.com/terms",
            "privacy": "https://currencylayer.com/privacy",
            "timestamp": 1633017600,
            "source": "USD",
            "quotes": {"USDUSD": 1.0, "USDEUR": 0.85},
            "error": None,
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = dummy_response
        mock_get.return_value = mock_resp

        test_date = datetime.date(2025, 1, 1)
        result = self.service.fetch_rates(date=test_date)
        self.assertEqual(result, dummy_response)

        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.service.API_URL_HISTORICAL)
        self.assertEqual(kwargs['params'].get('date'), test_date.strftime('%Y-%m-%d'))

    @patch('currency.services.CurrencyRateService.fetch_rates')
    def test_save_rates_creates_objects(self, mock_fetch_rates: MagicMock) -> None:
        """
        Check that currency objects and rate history records are created if data retrieval is successful.
        """
        dummy_response = {
            "success": True,
            "terms": "https://currencylayer.com/terms",
            "privacy": "https://currencylayer.com/privacy",
            "timestamp": 1633017600,
            "source": "USD",
            "quotes": {"USDUSD": 1.0, "USDEUR": 0.85},
            "error": None,
        }
        mock_fetch_rates.return_value = dummy_response

        # There are no currencies and no history records in the database before the test is executed
        self.assertEqual(Currency.objects.count(), 0)
        self.assertEqual(CurrencyRateHistory.objects.count(), 0)

        result = self.service.save_rates(date=datetime.date(2025, 1, 1))
        self.assertTrue(result)

        # Check that new currencies have been created
        self.assertTrue(Currency.objects.filter(code="USD").exists())
        self.assertTrue(Currency.objects.filter(code="EUR").exists())

        # Check that history records have been created for both courses
        self.assertEqual(CurrencyRateHistory.objects.count(), 2)

    @patch('currency.services.CurrencyRateService.fetch_rates')
    def test_save_rates_error_in_fetch(self, mock_fetch_rates: MagicMock) -> None:
        """
        If fetch_rates returns None (data fetch error), save_rates should return False.
        """
        mock_fetch_rates.return_value = None
        result = self.service.save_rates(date=datetime.date(2025, 1, 1))
        self.assertFalse(result)

    @patch('currency.services.CurrencyRateService.save_rates')
    def test_check_or_fetch_currency_data_already_exists(self, mock_save_rates: MagicMock) -> None:
        """
        If a history record already exists for a given date, save_rates is not called.
        """
        test_date = datetime.date(2025, 1, 1)
        # Create the currency and the corresponding history record
        currency = Currency.objects.create(code="EUR")
        CurrencyRateHistory.objects.create(
            currency=currency,
            per_usd=0.85,
            date=datetime.datetime(2025, 1, 1, tzinfo=timezone.utc)
        )

        result = self.service.check_or_fetch_currency_data(date=test_date)
        self.assertTrue(result)
        mock_save_rates.assert_not_called()

    @patch('currency.services.CurrencyRateService.save_rates')
    def test_check_or_fetch_currency_data_not_exists(self, mock_save_rates: MagicMock) -> None:
        """
        If there is no history record for a given date, save_rates must be called.
        """
        test_date = datetime.date(2025, 1, 1)
        # Let's make sure there's no history
        CurrencyRateHistory.objects.all().delete()

        self.service.check_or_fetch_currency_data(date=test_date)
        mock_save_rates.assert_called_once_with(test_date)

    def test_convert_timestamp_to_datetime(self) -> None:
        """
        Check that the _convert_timestamp_to_datetime method correctly converts timestamp to datetime.
        """
        timestamp = 1633017600
        dt = CurrencyRateService._convert_timestamp_to_datetime(timestamp)
        expected_dt = datetime.datetime.fromtimestamp(timestamp, tz=timezone.utc)
        self.assertEqual(dt, expected_dt)