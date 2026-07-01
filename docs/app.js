const CACHE_VERSION = "20260701-4";

const state = {
  candidates: new Map(),
  data: null
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;"
  }[char]));
}

function formatCandidateStatus(status) {
  const labels = {
    declared_candidate: "Declared candidate",
    party_designated: "Party-designated",
    primary_candidate: "Primary candidate",
    expected_candidate: "Expected candidate",
    poll_scenario_candidate: "Poll scenario",
    tracked_public_actor: "Tracked public actor",
    not_announced: "Not announced",
    withdrawn: "Withdrawn",
    needs_review: "Needs review"
  };

  return labels[status] || "Status pending";
}

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
      <strong>${escapeHtml(event.title)}</strong>
      <div class="meta">${escapeHtml(event.event_type)} · ${escapeHtml(event.event_date)}</div>
      <div class="meta">${escapeHtml(event.location_name)}, ${escapeHtml(event.region)}</div>
      <hr>
      <div><strong>${escapeHtml(event.candidate_name)}</strong></div>
      <div class="meta">${escapeHtml(candidate.party || "")} · ${escapeHtml(candidate.bloc || "")}</div>
      <div class="meta">${poll}</div>
      <hr>
      <div class="meta">Source: <a href="${escapeHtml(event.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(event.source_name)}</a></div>
      <div class="meta">Verification: ${escapeHtml(event.verification_status)}</div>
    </div>
  `;
}

function renderWire(events) {
  const wire = document.getElementById("eventWire");
  wire.innerHTML = events.map((event) => {
    const candidate = candidateById(event.candidate_id);
    return `
      <article class="event-item">
        <strong>${escapeHtml(event.title)}</strong>
        <div class="meta">${escapeHtml(event.event_date)} · ${escapeHtml(event.location_name)}</div>
        <div class="meta">
          <span class="color-chip" style="display:inline-block;background:${candidate.color_hex || "#38bdf8"}"></span>
          ${escapeHtml(event.candidate_name)} · ${escapeHtml(event.event_type)}
        </div>
      </article>
    `;
  }).join("");
}

function renderCandidatePollLine(candidate) {
  const hasLatestPoll = candidate.latest_poll !== null && candidate.latest_poll !== undefined;
  const hasComparableChange = candidate.poll_change !== null && candidate.poll_change !== undefined;

  if (!hasLatestPoll) {
    return "Poll change pending verified comparable poll";
  }

  const unit = candidate.poll_unit || "%";
  const latest = `${candidate.latest_poll}${unit}`;

  if (!hasComparableChange) {
    return `Latest verified poll: ${escapeHtml(latest)} · change pending comparable poll`;
  }

  return `Latest verified poll: ${escapeHtml(latest)} · change vs previous comparable: ${formatChange(candidate.poll_change)}`;
}

function renderCandidates(candidates) {
  const list = document.getElementById("candidateList");
  list.innerHTML = candidates.map((candidate) => `
    <article class="candidate-item">
      <div class="candidate-row">
        <span class="color-chip" style="background:${candidate.color_hex}"></span>
        <strong>${escapeHtml(candidate.display_name)}</strong>
      </div>
      <div class="meta">${escapeHtml(candidate.party)} · ${escapeHtml(candidate.bloc)}</div>
      <div class="meta">${escapeHtml(formatCandidateStatus(candidate.current_status))}</div>
      <div class="meta">${renderCandidatePollLine(candidate)}</div>
    </article>
  `).join("");
}

function renderPollCard(poll, pollStatus) {
  const card = document.getElementById("pollCard");

  if (!pollStatus || pollStatus.status_label === "no_staged_notices") {
    card.innerHTML = `
      <div class="pending-card poll-notice-card">
        <strong>Poll notices pending verified public source</strong>
        <p class="meta" style="margin-top:8px">
          This panel will show public poll notices after source and reuse conditions are reviewed. Placeholder poll values are not displayed in the public prototype.
        </p>
      </div>
    `;
    return;
  }

  const total = pollStatus.total_staged_notices ?? 0;
  const highPriority = pollStatus.high_priority_review_count ?? 0;
  const canonicalMetadata = pollStatus.canonical_poll_metadata_rows ?? 0;
  const canonicalResults = pollStatus.canonical_poll_result_rows ?? 0;
  const valuesExtracted = pollStatus.candidate_level_values_extracted ? "Yes" : "No";

  const metadataReview = pollStatus.metadata_review_status || {};
  const metadataRows = metadataReview.total_review_rows ?? 0;
  const metadataPending = metadataReview.pending_review_count ?? 0;
  const metadataReady = metadataReview.ready_for_canonical_metadata_count ?? 0;
  const metadataReviewLine = metadataRows ? `
      <p class="meta">
        Metadata review queue: ${metadataRows} metadata-only high-priority rows. ${metadataPending} pending review. ${metadataReady} ready for canonical metadata.
      </p>
    ` : "";

  const mediaDiscovery = pollStatus.media_discovery_status || {};
  const mediaRows = mediaDiscovery.total_media_mentions ?? 0;
  const mediaFeeds = mediaDiscovery.query_feed_count ?? 0;
  const mediaHigh = mediaDiscovery.high_priority_count ?? 0;
  const mediaPending = mediaDiscovery.pending_review_count ?? 0;
  const mediaPromoted = mediaDiscovery.promote_to_metadata_review_count ?? 0;
  const mediaValuesExtracted = mediaDiscovery.candidate_level_values_extracted ? "Yes" : "No";
  const mediaPromotionLine = mediaPromoted ? ` ${mediaPromoted} promoted to metadata review.` : "";
  const mediaDiscoveryLine = mediaRows ? `
      <p class="meta">
        Media discovery: ${mediaRows} staged article mentions from ${mediaFeeds} query feeds. ${mediaHigh} high priority.${mediaPromotionLine} ${mediaPending} pending review. Candidate-level values extracted: ${mediaValuesExtracted}.
      </p>
    ` : "";

  const examples = (pollStatus.high_priority_examples || []).slice(0, 2).map((row) => `
    <li style="margin-top:6px">
      <a href="${escapeHtml(row.notice_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.link_text)}</a>
    </li>
  `).join("");

  card.innerHTML = `
    <div class="pending-card poll-notice-card">
      <strong>Poll notice watcher active</strong>
      <p class="meta" style="margin-top:8px">
        ${total} Commission des sondages notice candidates are staged for review. ${highPriority} are high-priority likely presidential voting-intention notices.
      </p>
      <p class="meta">
        Canonical poll metadata rows: ${canonicalMetadata}. Candidate poll result rows: ${canonicalResults}.
      </p>
      <p class="meta">
        Candidate-level values extracted: ${valuesExtracted}.
      </p>
      ${metadataReviewLine}
      ${mediaDiscoveryLine}
      ${examples ? `
        <p class="meta" style="margin-top:10px"><strong>Review queue examples</strong></p>
        <ul class="meta" style="margin:6px 0 0 18px; padding:0">${examples}</ul>
      ` : ""}
      <p class="meta" style="margin-top:10px">
        Poll percentages remain hidden until source, method, and reuse conditions are reviewed.
      </p>
    </div>
  `;
}


function formatDocumentType(value) {
  const text = (value || "official_document").replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function renderOfficialDocuments(documents) {
  const list = document.getElementById("officialDocuments");

  if (!list) {
    return;
  }

  const items = documents || [];

  if (!items.length) {
    list.innerHTML = `
      <article class="document-card">
        <h3>No official documents surfaced yet</h3>
        <p class="meta">Official-document rows will appear here after export.</p>
      </article>
    `;
    return;
  }

  list.innerHTML = items.map((doc) => {
    const publicationDate = doc.publication_date
      ? ` · ${escapeHtml(doc.publication_date)}`
      : "";

    const summary = doc.summary_plain
      ? `<p class="document-summary">${escapeHtml(doc.summary_plain)}</p>`
      : "";

    return `
      <article class="document-card">
        <h3>${escapeHtml(doc.title)}</h3>
        <p class="document-meta">
          ${escapeHtml(doc.institution)} · ${escapeHtml(formatDocumentType(doc.document_type))}${publicationDate}
        </p>
        ${summary}
        <p class="document-meta">
          ${escapeHtml(doc.verification_status || "verification pending")}
        </p>
        <a class="document-link" href="${escapeHtml(doc.url)}" target="_blank" rel="noopener">
          Open source
        </a>
      </article>
    `;
  }).join("");
}

function initMap(data) {
  const map = L.map("map", {
    zoomControl: true,
    scrollWheelZoom: true,
    zoomSnap: 0.25,
    zoomDelta: 0.25,
  });

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 19,
  }).addTo(map);

  const eventBounds = [];

  (data.events || []).forEach((event) => {
    const latitude = Number(event.latitude);
    const longitude = Number(event.longitude);

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      return;
    }

    const candidate = candidateById(event.candidate_id);
    const color = candidate.color_hex || "#38bdf8";

    L.marker([latitude, longitude], {
      icon: createMarkerIcon(color),
    })
      .addTo(map)
      .bindPopup(popupHtml(event));

    eventBounds.push([latitude, longitude]);
  });

  function fitEventBounds() {
    if (eventBounds.length === 0) {
      map.setView([46.7, 2.4], 5.25);
      return;
    }

    if (eventBounds.length === 1) {
      map.setView(eventBounds[0], 6);
      return;
    }

    map.fitBounds(eventBounds, {
      paddingTopLeft: [36, 36],
      paddingBottomRight: [36, 36],
      maxZoom: 6,
    });
  }

  fitEventBounds();

  setTimeout(() => {
    map.invalidateSize();
    fitEventBounds();
  }, 150);

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      map.invalidateSize();
      fitEventBounds();
    }, 160);
  });
}


function formatTimestamp(value) {
  if (!value) return "not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function renderUpdatedAt(data) {
  const datasetUpdatedAt = data.dataset_updated_at || data.updated_at;
  const pollNoticeDetectedAt = data.poll_notice_latest_detected_at || data.poll_notice_status?.latest_detected_at;

  const parts = [`Dataset updated: ${formatTimestamp(datasetUpdatedAt)}`];

  if (pollNoticeDetectedAt && pollNoticeDetectedAt !== datasetUpdatedAt) {
    parts.push(`Poll notices detected: ${formatTimestamp(pollNoticeDetectedAt)}`);
  }

  document.getElementById("updatedAt").textContent = parts.join(" · ");
}

async function boot() {
  const response = await fetch(`./data/dashboard_sample.json?v=${CACHE_VERSION}`);
  const data = await response.json();
  state.data = data;
  data.candidates.forEach((candidate) => {
    state.candidates.set(candidate.candidate_id, candidate);
  });

  renderUpdatedAt(data);

  initMap(data);
  renderWire(data.events);
  renderCandidates(data.candidates);
  renderPollCard(data.latest_poll, data.poll_notice_status);
  renderOfficialDocuments(data.official_documents);
}

boot().catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML("beforeend", `<pre style="padding:16px;color:#fb7185">${escapeHtml(error.message)}</pre>`);
});
