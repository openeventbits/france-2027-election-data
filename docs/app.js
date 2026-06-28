const state = {
  candidates: new Map(),
  data: null
};

function formatChange(value) {
  if (value > 0) return `<span class="change-up">+${value}</span>`;
  if (value < 0) return `<span class="change-down">${value}</span>`;
  return `<span class="change-flat">0</span>`;
}

function candidateById(id) {
  return state.candidates.get(id) || {};
}

function markerHtml(color) {
  return `
    <div style="
      width: 18px;
      height: 18px;
      border-radius: 999px;
      background: ${color};
      border: 2px solid rgba(255,255,255,0.9);
      box-shadow: 0 0 20px ${color};
    "></div>
  `;
}

function createMarkerIcon(color) {
  return L.divIcon({
    html: markerHtml(color),
    className: "candidate-marker",
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    popupAnchor: [0, -10]
  });
}

function popupHtml(event) {
  const candidate = candidateById(event.candidate_id);
  const poll = "Poll data pending verified public source";

  return `
    <div class="popup-card">
      <strong>${event.title}</strong>
      <div class="meta">${event.event_type} · ${event.event_date}</div>
      <div class="meta">${event.location_name}, ${event.region}</div>
      <hr>
      <div><strong>${event.candidate_name}</strong></div>
      <div class="meta">${candidate.party || ""} · ${candidate.bloc || ""}</div>
      <div class="meta">${poll}</div>
      <hr>
      <div class="meta">Source: <a href="${event.source_url}" target="_blank" rel="noreferrer">${event.source_name}</a></div>
      <div class="meta">Verification: ${event.verification_status}</div>
    </div>
  `;
}

function renderWire(events) {
  const wire = document.getElementById("eventWire");
  wire.innerHTML = events.map((event) => {
    const candidate = candidateById(event.candidate_id);
    return `
      <article class="event-item">
        <strong>${event.title}</strong>
        <div class="meta">${event.event_date} · ${event.location_name}</div>
        <div class="meta">
          <span class="color-chip" style="display:inline-block;background:${candidate.color_hex || "#38bdf8"}"></span>
          ${event.candidate_name} · ${event.event_type}
        </div>
      </article>
    `;
  }).join("");
}

function renderCandidates(candidates) {
  const list = document.getElementById("candidateList");
  list.innerHTML = candidates.map((candidate) => `
    <article class="candidate-item">
      <div class="candidate-row">
        <span class="color-chip" style="background:${candidate.color_hex}"></span>
        <strong>${candidate.display_name}</strong>
      </div>
      <div class="meta">${candidate.party} · ${candidate.bloc}</div>
      <div class="meta">
        Poll data pending verified public source
      </div>
    </article>
  `).join("");
}

function renderPollCard(poll) {
  const card = document.getElementById("pollCard");
  card.innerHTML = `
    <div class="pending-card">
      <strong>Poll notices pending verified public source</strong>
      <p class="meta" style="margin-top:8px">
        This panel will show public poll notices after source and reuse conditions are reviewed. Placeholder poll values are not displayed in the public prototype.
      </p>
    </div>
  `;
}

function initMap(data) {
  const map = L.map("map", {
    zoomControl: true,
    scrollWheelZoom: true,
    zoomSnap: 0.25,
    zoomDelta: 0.25
  }).setView([46.75, 2.35], 5.95);

  window.addEventListener("resize", () => map.invalidateSize());
  setTimeout(() => map.invalidateSize(), 150);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 19
  }).addTo(map);

  data.events.forEach((event) => {
    const candidate = candidateById(event.candidate_id);
    const color = candidate.color_hex || "#38bdf8";
    L.marker([event.latitude, event.longitude], {
      icon: createMarkerIcon(color)
    })
      .addTo(map)
      .bindPopup(popupHtml(event));
  });
}

async function boot() {
  const response = await fetch("./data/dashboard_sample.json");
  const data = await response.json();
  state.data = data;
  data.candidates.forEach((candidate) => {
    state.candidates.set(candidate.candidate_id, candidate);
  });

  document.getElementById("updatedAt").textContent = new Date(data.updated_at).toLocaleString();

  initMap(data);
  renderWire(data.events);
  renderCandidates(data.candidates);
  renderPollCard(data.latest_poll);
}

boot().catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML("beforeend", `<pre style="padding:16px;color:#fb7185">${error.message}</pre>`);
});

