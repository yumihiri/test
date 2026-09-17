(function () {
  const CENTER = [36.3418, 140.4468]; // 水戸駅付近
  const config = window.SPOT_REGISTER_CONFIG;

  const map = L.map('map', { zoomControl: true }).setView(CENTER, 14);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 20,
    attribution:
      '地図データ: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  }).addTo(map);

  const latInput = document.getElementById('id_latitude');
  const lngInput = document.getElementById('id_longitude');
  const locText = document.getElementById('loc-text');
  const submitBtn = document.getElementById('submit-btn');
  const geocodeMessage = document.getElementById('geocode-message');

  let marker = null;

  function setPosition(lat, lng) {
    latInput.value = lat;
    lngInput.value = lng;
    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      marker = L.marker([lat, lng], { draggable: true }).addTo(map);
      marker.on('dragend', () => {
        const pos = marker.getLatLng();
        setPosition(pos.lat, pos.lng);
      });
    }
    map.setView([lat, lng], 16);
    locText.textContent = `緯度 ${Number(lat).toFixed(5)} / 経度 ${Number(lng).toFixed(5)}（設定済み）`;
    submitBtn.disabled = false;
  }

  map.on('click', (e) => {
    setPosition(e.latlng.lat, e.latlng.lng);
  });

  document.getElementById('geocode-btn').addEventListener('click', () => {
    const address = document.getElementById('id_address').value.trim();
    geocodeMessage.textContent = '';
    if (!address) {
      geocodeMessage.textContent = '住所を入力してください。';
      return;
    }
    geocodeMessage.textContent = '検索中…';
    const body = new URLSearchParams({ address });
    fetch(config.geocodeUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': config.csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    })
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) {
          geocodeMessage.textContent = data.error || '検索に失敗しました。地図をクリックして位置を指定してください。';
          return;
        }
        geocodeMessage.textContent = '位置を特定しました。ずれている場合は地図をクリックして調整してください。';
        setPosition(data.lat, data.lng);
      })
      .catch(() => {
        geocodeMessage.textContent = '通信エラーが発生しました。地図をクリックして位置を指定してください。';
      });
  });
})();
