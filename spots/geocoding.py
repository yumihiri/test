import requests
from django.conf import settings


class GeocodingError(Exception):
    pass


def geocode_address(address):
    """住所文字列から (latitude, longitude) を返す。国土地理院 AddressSearch API を利用。

    見つからない場合や通信エラーの場合は GeocodingError を送出する。
    呼び出し側で手動ピン指定へのフォールバックを用意すること。
    """
    try:
        response = requests.get(
            settings.GSI_GEOCODE_URL,
            params={"q": address},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError(f"ジオコーディングAPIへの接続に失敗しました: {exc}") from exc

    results = response.json()
    if not results:
        raise GeocodingError("住所から位置情報を取得できませんでした。地図上でピンを指定してください。")

    # GSI API は [経度, 緯度] の順で geometry.coordinates を返す
    lng, lat = results[0]["geometry"]["coordinates"]
    return lat, lng
