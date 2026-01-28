/* eslint-disable no-alert */
(() => {
  const STORAGE_KEY = "tcc_visible_osa_experimento_leds_v1";

  const DUTY_CYCLES = Array.from({ length: 20 }, (_, i) => (i + 1) * 5); // 5..100
  const EQUIPMENTS = [
    { id: "osa_visivel", label: "OSA Visível", tbodyId: "tbody-osa" },
    { id: "thorlabs", label: "ThorLabs", tbodyId: "tbody-thorlabs" },
  ];

  const COLORS = [
    { id: "green", label: "Verde", nmPlaceholder: "ex: 516.1", intPlaceholder: "ex: 177.85" },
    { id: "red", label: "Vermelho", nmPlaceholder: "ex: 637.7", intPlaceholder: "ex: 84.23" },
    { id: "blue", label: "Azul", nmPlaceholder: "ex: 468.2", intPlaceholder: "ex: 122.12" },
  ];

  /** @type {Record<string, any>} */
  let state = loadState();
  let currentEquipmentId = "osa_visivel";
  let saveTimer = /** @type {number | null} */ (null);

  const elSaveStatus = /** @type {HTMLSpanElement | null} */ (document.getElementById("save-status"));
  const btnExportCsv = /** @type {HTMLButtonElement | null} */ (document.getElementById("btn-export-csv"));
  const btnExportJson = /** @type {HTMLButtonElement | null} */ (document.getElementById("btn-export-json"));
  const fileImportJson = /** @type {HTMLInputElement | null} */ (document.getElementById("file-import-json"));
  const btnClearCurrent = /** @type {HTMLButtonElement | null} */ (document.getElementById("btn-clear-current"));

  const tabOsa = /** @type {HTMLButtonElement | null} */ (document.getElementById("tab-osa"));
  const tabThorlabs = /** @type {HTMLButtonElement | null} */ (document.getElementById("tab-thorlabs"));
  const panelOsa = /** @type {HTMLElement | null} */ (document.getElementById("panel-osa"));
  const panelThorlabs = /** @type {HTMLElement | null} */ (document.getElementById("panel-thorlabs"));

  function defaultState() {
    const data = {};
    for (const eq of EQUIPMENTS) {
      data[eq.id] = {};
      for (const duty of DUTY_CYCLES) {
        data[eq.id][String(duty)] = {};
        for (const c of COLORS) {
          data[eq.id][String(duty)][c.id] = { peak_nm: "", intensity: "" };
        }
      }
    }
    return {
      version: 1,
      updatedAt: null,
      data,
    };
  }

  function safeParseJson(text) {
    try {
      return { ok: true, value: JSON.parse(text) };
    } catch (e) {
      return { ok: false, error: e };
    }
  }

  function loadState() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState();
    const parsed = safeParseJson(raw);
    if (!parsed.ok) return defaultState();

    const loaded = parsed.value;
    const base = defaultState();

    // Merge only expected shape.
    for (const eq of EQUIPMENTS) {
      for (const duty of DUTY_CYCLES) {
        for (const c of COLORS) {
          const v =
            loaded?.data?.[eq.id]?.[String(duty)]?.[c.id] ??
            loaded?.[eq.id]?.[String(duty)]?.[c.id]; // tolerate older shape
          if (v && typeof v === "object") {
            if (typeof v.peak_nm === "string") base.data[eq.id][String(duty)][c.id].peak_nm = v.peak_nm;
            if (typeof v.intensity === "string")
              base.data[eq.id][String(duty)][c.id].intensity = v.intensity;
          }
        }
      }
    }

    base.updatedAt = typeof loaded?.updatedAt === "string" ? loaded.updatedAt : null;
    return base;
  }

  function setSaveStatus(text) {
    if (!elSaveStatus) return;
    elSaveStatus.textContent = text;
  }

  function formatDateTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "—";
    return d.toLocaleString("pt-BR");
  }

  function scheduleSave() {
    setSaveStatus("Salvando…");
    if (saveTimer) window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(() => {
      state.updatedAt = new Date().toISOString();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      setSaveStatus(`Salvo em ${formatDateTime(state.updatedAt)}`);
      saveTimer = null;
    }, 250);
  }

  function downloadText(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function escapeCsvCell(value) {
    const s = String(value ?? "");
    // Always quote to be safe with decimal commas, etc.
    return `"${s.replaceAll('"', '""')}"`;
  }

  function buildCsvForEquipment(eqId) {
    const headers = [
      "DutyCycle_percent",
      "Green_peak_nm",
      "Green_intensity",
      "Red_peak_nm",
      "Red_intensity",
      "Blue_peak_nm",
      "Blue_intensity",
    ];

    const rows = [headers.map(escapeCsvCell).join(",")];

    for (const duty of DUTY_CYCLES) {
      const d = state.data[eqId][String(duty)];
      const row = [
        duty,
        d.green.peak_nm,
        d.green.intensity,
        d.red.peak_nm,
        d.red.intensity,
        d.blue.peak_nm,
        d.blue.intensity,
      ];
      rows.push(row.map(escapeCsvCell).join(","));
    }

    return rows.join("\n");
  }

  function applyEquipmentTab(eqId) {
    currentEquipmentId = eqId;

    if (tabOsa && tabThorlabs) {
      const isOsa = eqId === "osa_visivel";
      tabOsa.setAttribute("aria-selected", String(isOsa));
      tabThorlabs.setAttribute("aria-selected", String(!isOsa));
    }

    if (panelOsa && panelThorlabs) {
      if (eqId === "osa_visivel") {
        panelOsa.classList.remove("panel--hidden");
        panelThorlabs.classList.add("panel--hidden");
      } else {
        panelThorlabs.classList.remove("panel--hidden");
        panelOsa.classList.add("panel--hidden");
      }
    }
  }

  function buildInput({ eqId, duty, colorId, field }) {
    const input = document.createElement("input");
    input.type = "number";
    input.inputMode = "decimal";
    input.step = "any";

    input.dataset.eq = eqId;
    input.dataset.duty = String(duty);
    input.dataset.color = colorId;
    input.dataset.field = field;

    const colorMeta = COLORS.find((c) => c.id === colorId);
    if (field === "peak_nm") {
      input.placeholder = colorMeta?.nmPlaceholder ?? "nm";
      input.min = "0";
    } else {
      input.placeholder = colorMeta?.intPlaceholder ?? "—";
    }

    const v = state.data[eqId][String(duty)][colorId][field];
    input.value = v === "" ? "" : v;

    input.addEventListener("input", () => {
      const next = input.value;
      state.data[eqId][String(duty)][colorId][field] = next;
      scheduleSave();
    });

    return input;
  }

  function buildTableBody(eqId, tbodyId) {
    const tbody = /** @type {HTMLTableSectionElement | null} */ (document.getElementById(tbodyId));
    if (!tbody) return;

    tbody.textContent = "";

    for (const duty of DUTY_CYCLES) {
      const tr = document.createElement("tr");

      const tdDuty = document.createElement("td");
      tdDuty.className = "sticky-col";
      tdDuty.textContent = String(duty);
      tr.appendChild(tdDuty);

      for (const color of COLORS) {
        const tdNm = document.createElement("td");
        tdNm.appendChild(buildInput({ eqId, duty, colorId: color.id, field: "peak_nm" }));
        tr.appendChild(tdNm);

        const tdInt = document.createElement("td");
        tdInt.appendChild(buildInput({ eqId, duty, colorId: color.id, field: "intensity" }));
        tr.appendChild(tdInt);
      }

      tbody.appendChild(tr);
    }
  }

  function renderAll() {
    for (const eq of EQUIPMENTS) buildTableBody(eq.id, eq.tbodyId);
    setSaveStatus(state.updatedAt ? `Salvo em ${formatDateTime(state.updatedAt)}` : "Sem alterações ainda");
    applyEquipmentTab(currentEquipmentId);
  }

  function clearEquipment(eqId) {
    for (const duty of DUTY_CYCLES) {
      for (const c of COLORS) {
        state.data[eqId][String(duty)][c.id].peak_nm = "";
        state.data[eqId][String(duty)][c.id].intensity = "";
      }
    }
  }

  function importStateFromObject(obj) {
    // Accept either full object (with data/updatedAt) or "data-like".
    const base = defaultState();
    const incoming = obj?.data ? obj : { data: obj };

    for (const eq of EQUIPMENTS) {
      for (const duty of DUTY_CYCLES) {
        for (const c of COLORS) {
          const src = incoming?.data?.[eq.id]?.[String(duty)]?.[c.id];
          if (!src || typeof src !== "object") continue;
          if (typeof src.peak_nm === "string") base.data[eq.id][String(duty)][c.id].peak_nm = src.peak_nm;
          if (typeof src.intensity === "string") base.data[eq.id][String(duty)][c.id].intensity = src.intensity;
        }
      }
    }

    base.updatedAt = new Date().toISOString();
    return base;
  }

  // Wire UI
  if (tabOsa) tabOsa.addEventListener("click", () => applyEquipmentTab("osa_visivel"));
  if (tabThorlabs) tabThorlabs.addEventListener("click", () => applyEquipmentTab("thorlabs"));

  if (btnExportCsv) {
    btnExportCsv.addEventListener("click", () => {
      const csv = buildCsvForEquipment(currentEquipmentId);
      const ts = new Date().toISOString().replaceAll(":", "-");
      downloadText(`dados_${currentEquipmentId}_${ts}.csv`, csv, "text/csv;charset=utf-8");
    });
  }

  if (btnExportJson) {
    btnExportJson.addEventListener("click", () => {
      const ts = new Date().toISOString().replaceAll(":", "-");
      downloadText(`dados_todos_${ts}.json`, JSON.stringify(state, null, 2), "application/json;charset=utf-8");
    });
  }

  if (fileImportJson) {
    fileImportJson.addEventListener("change", async () => {
      const file = fileImportJson.files?.[0];
      if (!file) return;
      const text = await file.text();
      const parsed = safeParseJson(text);
      if (!parsed.ok) {
        alert("JSON inválido. Verifique o arquivo e tente novamente.");
        fileImportJson.value = "";
        return;
      }
      state = importStateFromObject(parsed.value);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      renderAll();
      fileImportJson.value = "";
      alert("Importação concluída. Os dados foram carregados e salvos.");
    });
  }

  if (btnClearCurrent) {
    btnClearCurrent.addEventListener("click", () => {
      const name = currentEquipmentId === "osa_visivel" ? "OSA Visível" : "ThorLabs";
      const ok = confirm(`Tem certeza que deseja apagar todos os dados do equipamento: ${name}?`);
      if (!ok) return;
      clearEquipment(currentEquipmentId);
      scheduleSave();
      renderAll();
    });
  }

  // Initial render
  renderAll();
})();

