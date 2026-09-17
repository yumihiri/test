(function () {
  const CENTER = [36.3418, 140.4468]; // 水戸駅付近
  const categories = JSON.parse(document.getElementById('categories-data').textContent);
  const spots = JSON.parse(document.getElementById('spots-data').textContent);
  const activeCategories = new Set(categories.map((c) => c.id));

  const categoryOf = (id) => categories.find((c) => c.id === id);

  const map = L.map('map', { zoomControl: true }).setView(CENTER, 14);
  L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution:
      '地図: <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
  }).addTo(map);

  const markerLayer = L.layerGroup().addTo(map);

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function statusLabel(status) {
    if (status === 'pending') return '<span class="status-badge status-pending">承認待ち</span>';
    if (status === 'rejected') return '<span class="status-badge status-rejected">却下</span>';
    return '';
  }

  function renderMarkers() {
    markerLayer.clearLayers();
    spots
      .filter((s) => activeCategories.has(s.categoryId))
      .forEach((spot) => {
        const cat = categoryOf(spot.categoryId);
        if (!cat) return;
        const cls = spot.status === 'pending' ? 'pending' : spot.status === 'rejected' ? 'rejected' : '';
        const html = `<div class="spot-marker ${cls}" style="background:${cat.color}">${cat.icon_class}</div>`;
        const marker = L.marker([spot.lat, spot.lng], {
          icon: L.divIcon({ className: '', html, iconSize: [30, 30], iconAnchor: [15, 15] }),
        });
        const ratingText = spot.avgRating ? `★${spot.avgRating}（${spot.reviewCount}件）` : '評価なし';
        marker.bindPopup(`
          <strong>${cat.icon_class} ${escapeHtml(spot.name)}</strong><br>
          ${statusLabel(spot.status)}
          <div style="font-size:.8rem;margin:4px 0;">${ratingText}</div>
          <a href="${spot.detailUrl}">詳細を見る →</a>
        `);
        marker.addTo(markerLayer);
      });
  }

  function renderSidebar() {
    const el = document.getElementById('cat-list');
    el.innerHTML = categories
      .map(
        (c) => `
      <li>
        <input type="checkbox" checked data-cat="${c.id}">
        <span class="cat-dot" style="background:${c.color}">${c.icon_class}</span> ${escapeHtml(c.name)}
      </li>`
      )
      .join('');
    el.querySelectorAll('input[type=checkbox]').forEach((cb) => {
      cb.addEventListener('change', () => {
        const id = parseInt(cb.dataset.cat, 10);
        if (cb.checked) activeCategories.add(id);
        else activeCategories.delete(id);
        renderMarkers();
      });
    });
  }

  renderSidebar();
  renderMarkers();
})();
