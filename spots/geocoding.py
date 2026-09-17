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
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError(
            "ジオコーディングAPIの応答がありませんでした。地図をクリックして手動でピンを指定してください。"
        ) from exc

    results = response.json()
    if not results:
        raise GeocodingError("住所から位置情報を取得できませんでした。地図上でピンを指定してください。")

    # GSI API は [経度, 緯度] の順で geometry.coordinates を返す
    lng, lat = results[0]["geometry"]["coordinates"]
    return lat, lng


def reverse_geocode(lat, lng):
    """緯度経度から市区町村レベルの住所文字列を返す。国土地理院 逆ジオコーディングAPI を利用。

    番地までは取得できないため、あくまで下書き用の目安。ユーザーが登録前に編集できる前提。
    見つからない場合や通信エラーの場合は GeocodingError を送出する。
    """
    try:
        response = requests.get(
            "https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress",
            params={"lon": lng, "lat": lat},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GeocodingError(
            "逆ジオコーディングAPIの応答がありませんでした。住所は手動で入力してください。"
        ) from exc

    data = response.json()
    result = data.get("results")
    municipality = result.get("lv01Nm") if result else None
    if not municipality:
        raise GeocodingError("この地点の住所を特定できませんでした。")
    return municipality
