import itertools
import json
import logging
import requests

from datetime import timezone, date as type_date, datetime
from django.conf import settings
from django.db import IntegrityError, transaction
from .models import Currency, CurrencyRateHistory
from .schemas import CurrencyResponse

logger = logging.getLogger(__name__)


class CurrencyRateService:
    API_URL_HISTORICAL = 'https://api.currencylayer.com/historical'
    API_URL_LIVE = 'https://api.currencylayer.com/live'

    def __init__(self) -> None:
        self.api_keys = itertools.cycle(settings.APILAYER_API_KEYS)

    @staticmethod
    def _get_headers(api_key: str) -> dict[str, str]:
        return {'access_key': api_key}

    def _make_request(self, url: str, params: dict[str, str]) -> CurrencyResponse | None:
        max_attempts = len(settings.APILAYER_API_KEYS)

        for _ in range(max_attempts):
            api_key = next(self.api_keys)

            try:
                response = requests.get(url, params=params | {'access_key': api_key}, timeout=10)
                data: CurrencyResponse = response.json()

                if not data.get('success', False):
                    logger.warning(f'API returned an error: {data.get('error', {})}')
                    continue

                return data

            except requests.exceptions.RequestException as e:
                logger.error(f'Request error to API: {e}')
                continue
            except json.decoder.JSONDecodeError as e:
                continue

        logger.error('All API keys have failed.')
        return None

    def fetch_rates(self, date: type_date | None = None) -> CurrencyResponse | None:
        params: dict[str, str] = {}

        if date and date != datetime.now().date():
            params['date'] = date.strftime('%Y-%m-%d')
            url = self.API_URL_HISTORICAL
        else:
            url = self.API_URL_LIVE

        return self._make_request(url, params)

    @staticmethod
    def _convert_timestamp_to_datetime(timestamp: int | None) -> datetime:
        if timestamp:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return datetime.now(timezone.utc)

    @staticmethod
    def _get_existing_currencies() -> dict[str, Currency]:
        return {currency.code: currency for currency in Currency.objects.all()}

    @staticmethod
    def _create_missing_currencies(existing_currencies: dict[str, Currency], target_currency_codes: list[str]) -> None:
        new_currencies = [Currency(code=code) for code in target_currency_codes if code not in existing_currencies]

        if new_currencies:
            Currency.objects.bulk_create(new_currencies)
            existing_currencies.update({currency.code: currency for currency in
                                        Currency.objects.filter(code__in=[c.code for c in new_currencies])})

    @staticmethod
    def _prepare_currency_rate_history_objects(existing_currencies: dict[str, Currency], data: CurrencyResponse,
                                               date_obj: datetime) -> list[CurrencyRateHistory]:
        currency_rate_history_objects = []

        for pair, rate in data.get('quotes', {}).items():
            target_currency_code = pair[3:]

            if target_currency_code in existing_currencies:
                currency_rate_history_objects.append(
                    CurrencyRateHistory(currency=existing_currencies[target_currency_code], per_usd=rate, date=date_obj)
                )
            else:
                logger.warning(f'Currency {target_currency_code} is missing in the database.')

        return currency_rate_history_objects

    @staticmethod
    def _save_currency_rate_history_objects(currency_rate_history_objects: list[CurrencyRateHistory]) -> None:
        if not currency_rate_history_objects:
            logger.info('No data to save.')
            return

        try:
            CurrencyRateHistory.objects.bulk_create(currency_rate_history_objects)
        except IntegrityError as e:
            logger.error(f'Bulk save error: {e}')
            for obj in currency_rate_history_objects:
                try:
                    obj.save()
                except IntegrityError as e:
                    logger.error(f'Error saving {obj.currency.code}: {e}')

    def save_rates(self, date: type_date | None = None) -> bool:
        data = self.fetch_rates(date)
        if not data or 'quotes' not in data:
            logger.error('Error fetching data from API.')
            return False

        date_obj = self._convert_timestamp_to_datetime(data.get('timestamp'))
        existing_currencies = self._get_existing_currencies()
        target_currency_codes = [pair[3:] for pair in data['quotes'].keys()]

        self._create_missing_currencies(existing_currencies, target_currency_codes)
        currency_rate_history_objects = self._prepare_currency_rate_history_objects(existing_currencies, data, date_obj)

        with transaction.atomic():
            self._save_currency_rate_history_objects(currency_rate_history_objects)

        return True

    def check_or_fetch_currency_data(self, date: type_date | None = None) -> bool:
        if not CurrencyRateHistory.objects.filter(date__date=date).exists():
            return self.save_rates(date)
        return True

