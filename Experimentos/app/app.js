/* eslint-disable no-alert */
(() => {
  const STORAGE_KEY = "tcc_visible_osa_experimento_leds_v2";

  const DUTY_CYCLES = Array.from({ length: 10 }, (_, i) => i + 1); // 1..10
  const NUM_TOMADAS = 5;
  const OSA_ESPECTROS = [
    { id: 1, label: "Combinado RGB" },
    { id: 2, label: "Canal R" },
    { id: 3, label: "Canal G" },
    { id: 4, label: "Canal B" },
  ];

  const COLORS = [
    { id: "green", label: "Verde", nmPlaceholder: "ex: 516.1", intPlaceholder: "ex: 177.85" },
    { id: "red", label: "Vermelho", nmPlaceholder: "ex: 637.7", intPlaceholder: "ex: 84.23" },
    { id: "blue", label: "Azul", nmPlaceholder: "ex: 468.2", intPlaceholder: "ex: 122.12" },
  ];

  let state = loadState();
  let currentEquipmentId = "osa_visivel";
  let currentTomada = 1;
  let currentEspectro = 1;
  let saveTimer = null;

  const elSaveStatus = document.getElementById("save-status");
  const cbPasteMode = document.getElementById("cb-paste-mode");
  const btnPasteClipboard = document.getElementById("btn-paste-clipboard");
  const btnExportCsv = document.getElementById("btn-export-csv");
  const btnExportJson = document.getElementById("btn-export-json");
  const fileImportJson = document.getElementById("file-import-json");
  const btnClearCurrent = document.getElementById("btn-clear-current");
  const tabOsa = document.getElementById("tab-osa");
  const tabThorlabs = document.getElementById("tab-thorlabs");
  const panelOsa = document.getElementById("panel-osa");
  const panelThorlabs = document.getElementById("panel-thorlabs");
  const osaSub = document.getElementById("osa-sub");
  const thorlabsSub = document.getElementById("thorlabs-sub");

  let pasteMode = false;
  let pasteValue = null;

  function defaultState() {
    const data = { osa_visivel: {}, thorlabs: {} };

    for (let t = 1; t <= NUM_TOMADAS; t++) {
      data.thorlabs[String(t)] = {};
      for (const duty of DUTY_CYCLES) {
        data.thorlabs[String(t)][String(duty)] = {};
        for (const c of COLORS) {
          data.thorlabs[String(t)][String(duty)][c.id] = { peak_nm: "", intensity: "" };
        }
      }

      data.osa_visivel[String(t)] = {};
      for (let e = 1; e <= OSA_ESPECTROS.length; e++) {
        data.osa_visivel[String(t)][String(e)] = {};
        for (const duty of DUTY_CYCLES) {
          data.osa_visivel[String(t)][String(e)][String(duty)] = {};
          for (const c of COLORS) {
            data.osa_visivel[String(t)][String(e)][String(duty)][c.id] = { peak_nm: "", intensity: "" };
          }
        }
      }
    }

    return { version: 2, updatedAt: null, data };
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

    if (loaded?.data?.osa_visivel) {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        const T = String(t);
        if (!loaded.data.osa_visivel[T]) continue;
        for (let e = 1; e <= OSA_ESPECTROS.length; e++) {
          const E = String(e);
          if (!loaded.data.osa_visivel[T][E]) continue;
          for (const duty of DUTY_CYCLES) {
            const D = String(duty);
            if (!loaded.data.osa_visivel[T][E][D]) continue;
            for (const c of COLORS) {
              const v = loaded.data.osa_visivel[T][E][D][c.id];
              if (v && typeof v === "object") {
                if (typeof v.peak_nm === "string") base.data.osa_visivel[T][E][D][c.id].peak_nm = v.peak_nm;
                if (typeof v.intensity === "string") base.data.osa_visivel[T][E][D][c.id].intensity = v.intensity;
              }
            }
          }
        }
      }
    }

    if (loaded?.data?.thorlabs) {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        const T = String(t);
        if (!loaded.data.thorlabs[T]) continue;
        for (const duty of DUTY_CYCLES) {
          const D = String(duty);
          if (!loaded.data.thorlabs[T][D]) continue;
          for (const c of COLORS) {
            const v = loaded.data.thorlabs[T][D][c.id];
            if (v && typeof v === "object") {
              if (typeof v.peak_nm === "string") base.data.thorlabs[T][D][c.id].peak_nm = v.peak_nm;
              if (typeof v.intensity === "string") base.data.thorlabs[T][D][c.id].intensity = v.intensity;
            }
          }
        }
      }
    }

    base.updatedAt = typeof loaded?.updatedAt === "string" ? loaded.updatedAt : null;
    return base;
  }

  function setSaveStatus(text) {
    if (elSaveStatus) elSaveStatus.textContent = text;
  }

  function isValidNumber(str) {
    if (typeof str !== "string") return false;
    const trimmed = str.trim();
    if (trimmed === "") return false;
    const n = parseFloat(trimmed.replace(",", "."));
    return Number.isFinite(n);
  }

  function exitPasteMode() {
    pasteMode = false;
    pasteValue = null;
    if (btnPasteClipboard) btnPasteClipboard.classList.remove("btn--paste-active");
    setSaveStatus(state.updatedAt ? `Salvo em ${formatDateTime(state.updatedAt)}` : "Sem alterações ainda");
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
    return `"${s.replaceAll('"', '""')}"`;
  }

  function getCurrentTableData() {
    if (currentEquipmentId === "osa_visivel") {
      return state.data.osa_visivel[String(currentTomada)][String(currentEspectro)];
    }
    return state.data.thorlabs[String(currentTomada)];
  }

  function buildCsvForCurrentTable() {
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
    const tableData = getCurrentTableData();
    if (!tableData) return rows.join("\n");

    for (const duty of DUTY_CYCLES) {
      const d = tableData[String(duty)];
      if (!d) continue;
      const row = [
        duty,
        d.green?.peak_nm ?? "",
        d.green?.intensity ?? "",
        d.red?.peak_nm ?? "",
        d.red?.intensity ?? "",
        d.blue?.peak_nm ?? "",
        d.blue?.intensity ?? "",
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
        if (osaSub) osaSub.classList.remove("sub-tabs--hidden");
        if (thorlabsSub) thorlabsSub.classList.add("sub-tabs--hidden");
      } else {
        panelThorlabs.classList.remove("panel--hidden");
        panelOsa.classList.add("panel--hidden");
        if (osaSub) osaSub.classList.add("sub-tabs--hidden");
        if (thorlabsSub) thorlabsSub.classList.remove("sub-tabs--hidden");
      }
    }

    updateTomadaEspectroButtons();
    renderCurrentTable();
  }

  function updateTomadaEspectroButtons() {
    const isOsa = currentEquipmentId === "osa_visivel";
    document.querySelectorAll("#osa-sub [data-tomada], #thorlabs-sub [data-tomada]").forEach((btn) => {
      const t = Number(btn.getAttribute("data-tomada"));
      btn.setAttribute("aria-selected", t === currentTomada ? "true" : "false");
    });
    document.querySelectorAll("#osa-sub [data-espectro]").forEach((btn) => {
      const esp = Number(btn.getAttribute("data-espectro"));
      btn.setAttribute("aria-selected", isOsa && esp === currentEspectro ? "true" : "false");
    });
  }

  function buildInput(params) {
    const { eqId, tomada, espectro, duty, colorId, field } = params;
    const input = document.createElement("input");
    input.type = "number";
    input.inputMode = "decimal";
    input.step = "any";
    input.dataset.eq = eqId;
    input.dataset.tomada = String(tomada);
    if (eqId === "osa_visivel") input.dataset.espectro = String(espectro);
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

    let value;
    if (eqId === "osa_visivel") {
      value = state.data.osa_visivel[String(tomada)][String(espectro)][String(duty)][colorId][field];
    } else {
      value = state.data.thorlabs[String(tomada)][String(duty)][colorId][field];
    }
    input.value = value === "" ? "" : value;

    input.addEventListener("input", () => {
      const next = input.value;
      if (eqId === "osa_visivel") {
        state.data.osa_visivel[String(tomada)][String(espectro)][String(duty)][colorId][field] = next;
      } else {
        state.data.thorlabs[String(tomada)][String(duty)][colorId][field] = next;
      }
      scheduleSave();
    });

    return input;
  }

  function renderCurrentTable() {
    const tbodyId = currentEquipmentId === "osa_visivel" ? "tbody-osa" : "tbody-thorlabs";
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    tbody.textContent = "";
    const tomada = currentTomada;
    const espectro = currentEspectro;
    const eqId = currentEquipmentId;

    for (const duty of DUTY_CYCLES) {
      const tr = document.createElement("tr");
      const tdDuty = document.createElement("td");
      tdDuty.className = "sticky-col";
      tdDuty.textContent = String(duty);
      tr.appendChild(tdDuty);

      for (const color of COLORS) {
        const tdNm = document.createElement("td");
        tdNm.appendChild(
          buildInput({
            eqId,
            tomada,
            espectro,
            duty,
            colorId: color.id,
            field: "peak_nm",
          })
        );
        tr.appendChild(tdNm);
        const tdInt = document.createElement("td");
        tdInt.appendChild(
          buildInput({
            eqId,
            tomada,
            espectro,
            duty,
            colorId: color.id,
            field: "intensity",
          })
        );
        tr.appendChild(tdInt);
      }
      tbody.appendChild(tr);
    }

    updateTomadaEspectroButtons();
  }

  function renderAll() {
    setSaveStatus(state.updatedAt ? `Salvo em ${formatDateTime(state.updatedAt)}` : "Sem alterações ainda");
    applyEquipmentTab(currentEquipmentId);
  }

  function clearEquipment(eqId) {
    if (eqId === "osa_visivel") {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        for (let e = 1; e <= OSA_ESPECTROS.length; e++) {
          for (const duty of DUTY_CYCLES) {
            for (const c of COLORS) {
              state.data.osa_visivel[String(t)][String(e)][String(duty)][c.id].peak_nm = "";
              state.data.osa_visivel[String(t)][String(e)][String(duty)][c.id].intensity = "";
            }
          }
        }
      }
    } else {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        for (const duty of DUTY_CYCLES) {
          for (const c of COLORS) {
            state.data.thorlabs[String(t)][String(duty)][c.id].peak_nm = "";
            state.data.thorlabs[String(t)][String(duty)][c.id].intensity = "";
          }
        }
      }
    }
  }

  function importStateFromObject(obj) {
    const base = defaultState();
    const incoming = obj?.data ? obj : { data: obj };
    if (!incoming.data) return base;

    if (incoming.data.osa_visivel) {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        const T = String(t);
        if (!incoming.data.osa_visivel[T]) continue;
        for (let e = 1; e <= OSA_ESPECTROS.length; e++) {
          const E = String(e);
          if (!incoming.data.osa_visivel[T][E]) continue;
          for (const duty of DUTY_CYCLES) {
            const D = String(duty);
            if (!incoming.data.osa_visivel[T][E][D]) continue;
            for (const c of COLORS) {
              const src = incoming.data.osa_visivel[T][E][D][c.id];
              if (!src || typeof src !== "object") continue;
              if (typeof src.peak_nm === "string") base.data.osa_visivel[T][E][D][c.id].peak_nm = src.peak_nm;
              if (typeof src.intensity === "string") base.data.osa_visivel[T][E][D][c.id].intensity = src.intensity;
            }
          }
        }
      }
    }

    if (incoming.data.thorlabs) {
      for (let t = 1; t <= NUM_TOMADAS; t++) {
        const T = String(t);
        if (!incoming.data.thorlabs[T]) continue;
        for (const duty of DUTY_CYCLES) {
          const D = String(duty);
          if (!incoming.data.thorlabs[T][D]) continue;
          for (const c of COLORS) {
            const src = incoming.data.thorlabs[T][D][c.id];
            if (!src || typeof src !== "object") continue;
            if (typeof src.peak_nm === "string") base.data.thorlabs[T][D][c.id].peak_nm = src.peak_nm;
            if (typeof src.intensity === "string") base.data.thorlabs[T][D][c.id].intensity = src.intensity;
          }
        }
      }
    }

    base.updatedAt = new Date().toISOString();
    return base;
  }

  if (cbPasteMode) {
    cbPasteMode.addEventListener("change", () => {
      if (btnPasteClipboard) btnPasteClipboard.disabled = !cbPasteMode.checked;
      if (!cbPasteMode.checked) exitPasteMode();
    });
  }
  if (btnPasteClipboard) {
    btnPasteClipboard.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (!isValidNumber(text)) {
          setSaveStatus("Área de transferência não contém número válido.");
          return;
        }
        const trimmed = text.trim().replace(",", ".");
        pasteValue = trimmed;
        pasteMode = true;
        btnPasteClipboard.classList.add("btn--paste-active");
        setSaveStatus(`Clique em uma célula para colar: ${trimmed}`);
      } catch (err) {
        setSaveStatus("Não foi possível ler a área de transferência (permissão ou navegador).");
      }
    });
  }
  document.addEventListener("click", (e) => {
    if (!pasteMode || pasteValue == null) return;
    const input = e.target.tagName === "INPUT" && e.target.dataset.eq && e.target.closest(".data-table") ? e.target : null;
    if (!input) return;
    input.value = pasteValue;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    exitPasteMode();
  });

  if (tabOsa) tabOsa.addEventListener("click", () => applyEquipmentTab("osa_visivel"));
  if (tabThorlabs) tabThorlabs.addEventListener("click", () => applyEquipmentTab("thorlabs"));

  document.querySelectorAll("#osa-sub [data-tomada]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentTomada = Number(btn.getAttribute("data-tomada"));
      renderCurrentTable();
    });
  });
  document.querySelectorAll("#osa-sub [data-espectro]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentEspectro = Number(btn.getAttribute("data-espectro"));
      renderCurrentTable();
    });
  });
  document.querySelectorAll("#thorlabs-sub [data-tomada]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentTomada = Number(btn.getAttribute("data-tomada"));
      renderCurrentTable();
    });
  });

  if (btnExportCsv) {
    btnExportCsv.addEventListener("click", () => {
      const csv = buildCsvForCurrentTable();
      const ts = new Date().toISOString().replaceAll(":", "-");
      let name = `dados_${currentEquipmentId}_tomada${currentTomada}`;
      if (currentEquipmentId === "osa_visivel") name += `_espectro${currentEspectro}`;
      name += `_${ts}.csv`;
      downloadText(name, csv, "text/csv;charset=utf-8");
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
      const ok = confirm(`Apagar todos os dados do equipamento: ${name}? (todas as tomadas e espectros)`);
      if (!ok) return;
      clearEquipment(currentEquipmentId);
      scheduleSave();
      renderAll();
    });
  }

  renderAll();
})();
