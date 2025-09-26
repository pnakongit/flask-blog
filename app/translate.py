from functools import lru_cache

import requests
from flask import current_app
from flask_babel import _  # NOQA


@lru_cache(maxsize=512)
def translate(text: str, source_language: str, dest_language: str) -> str:
    url = "https://api.cognitive.microsofttranslator.com/translate"
    api_key = current_app.config.get("MS_TRANSLATOR_KEY")
    api_region = current_app.config.get("MS_TRANSLATOR_REGION")

    if api_key is None or api_region is None:
        return _('Error: the translation service is not configured.')

    auth = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Ocp-Apim-Subscription-Region": api_region,
    }

    params = {
        "api-version": '3.0',
        "from": source_language,
        "to": dest_language,
    }

    response = requests.post(
        url,
        params=params,
        headers=auth,
        json=[{"Text": text}]
    )

    if response.status_code != 200:
        return _('Error: the translation service failed.')

    return response.json()[0]["translations"][0]["text"]
