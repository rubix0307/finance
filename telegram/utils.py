import hashlib
import hmac
import json
from operator import itemgetter
from typing import Optional
from urllib.parse import parse_qsl
from django.conf import settings

from user.models import User


def check_webapp_signature(init_data: str) -> tuple[bool, Optional[int]]:
    """
    Check incoming WebApp init data signature
    Source: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    user_id = None

    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return False, user_id

    if "hash" not in parsed_data:
        return False, user_id

    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=settings.TELEGRAM_BOT_TOKEN.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    result = calculated_hash == hash_

    if result:
        user_id = json.loads(parsed_data['user'])['id']

    return result, user_id


check_webapp_signature(init_data='user=%7B%22id%22%3A887832606%2C%22first_name%22%3A%22%D0%90%D1%80%D1%82%D0%B5%D0%BC%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22xx_rubix_xx%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FW97nRA54RtajobFQud_3vsnpQyKmB8cOoaPA13sS-QM.svg%22%7D&chat_instance=7188888625162796947&chat_type=private&auth_date=1744468067&signature=iZHF7l4qAWCjsnkXtxPdP57fK2v4W50kbqVEyfWycHIzPBuAeinYAHPAUPaZKGF-wjqqx7KMGgBX8Bcl_86nCQ&hash=5a71d2b68efa37fb1046394dd279c989d9a7a26297a236d0fdb92240d1789eb2')

def get_or_create_user(user_id: int) -> User:
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = User(
            id=user_id,
        )
        user.save(is_new=True)

    return user