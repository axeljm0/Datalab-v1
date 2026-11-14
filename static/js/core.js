/* ============================================================
   core.js — utilidades compartidas del laboratorio DataLab
   API wrapper, reproductor de animaciones, renderizadores SVG,
   fábrica de gráficos y notificaciones.
   ============================================================ */
"use strict";

/* ---------------- API REST ---------------- */
const API = {
  async request(url, options = {}) {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    let body = null;
    try { body = await response.json(); } catch { body = { success: false, error: "Respuesta no válida" }; }
    if (!response.ok || body.success === false) {
      const error = new Error(body.error || `Error ${response.status}`);
      error.payload = body;
      throw error;
    }
    return body.data;
  },
  get: (url) => API.request(url),
  post: (url, payload) => API.request(url, { method: "POST", body: JSON.stringify(payload ?? {}) }),
  del: (url) => API.request(url, { method: "DELETE" }),
};

/* ---------------- Utilidades DOM ---------------- */
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function toast(message, type = "") {
  const el = $("#toast");
  el.textContent = message;
  el.className = `toast ${type}`;
  el.style.display = "block";
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { el.style.display = "none"; }, 3500);
}

function fmt(value, digits = 3) {
  if (value === null || value === undefined) return "—";
  if (Number.isInteger(value)) return value.toLocaleString("es");
  return Number(value).toLocaleString("es", { maximumFractionDigits: digits });
}

/* ---------------- Reproductor de animaciones ----------------
   Reproduce una secuencia de pasos (frames) con controles de
   ejecutar / pausar / paso a paso / reiniciar y velocidad.
   Cada frame lo pinta la función render(frame, index).           */
class Player {
  constructor({ frames, render, onDone, baseDelay = 420 }) {
    this.frames = frames;
    this.render = render;
    this.onDone = onDone || (() => {});
    this.baseDelay = baseDelay;
    this.index = -1;
    this.timer = null;
    this.playing = false;
  }

  speed() {  // El slider va de 0 (lento) a 100 (rápido).
    const slider = $("#speedSlider");
    const percent = slider ? Number(slider.value) : 50;
    return this.baseDelay * Math.pow(0.02, percent / 100); // 420ms..8ms
  }

  renderStep() {
    if (this.index >= this.frames.length - 1) { this.pause(); this.onDone(); return; }
    this.index += 1;
    this.render(this.frames[this.index], this.index);
    this.updateLabel();
  }

  play() {
    if (this.playing) return;
    if (this.index >= this.frames.length - 1) this.index = -1; // Reinicio al reproducir.
    this.playing = true;
    const tick = () => {
      if (!this.playing) return;
      if (this.index >= this.frames.length - 1) { this.pause(); this.onDone(); return; }
      this.renderStep();
      this.timer = setTimeout(tick, this.speed());
    };
    tick();
  }

  pause() { this.playing = false; clearTimeout(this.timer); }

  stepForward() { this.pause(); this.renderStep(); }

  reset() { this.pause(); this.index = -1; this.render(null, -1); this.updateLabel(); }

  updateLabel() {
    const label = $("#stepLabel");
    if (label) label.textContent = `${Math.max(0, this.index + 1)} / ${this.frames.length}`;
  }

  bindControls() {
    $("#playBtn")?.addEventListener("click", () => this.play());
    $("#pauseBtn")?.addEventListener("click", () => this.pause());
    $("#stepBtn")?.addEventListener("click", () => this.stepForward());
    $("#resetBtn")?.addEventListener("click", () => this.reset());
    $("#speedSlider")?.addEventListener("input", () => {});
  }
}

/* Sincroniza un conjunto de elementos con las clases de resaltado. */
function setHighlight(elements, indices, className) {
  elements.forEach((el, i) => el.classList.toggle(className, indices.includes(i)));
}

/* ---------------- Render de árboles (SVG) ----------------
   Recibe {nodes, edges} con ids tipo heap-binario (padre p,
   hijos 2p+1 / 2p+2) y calcula posiciones por profundidad. */
function renderTreeSVG(container, data, { nodeRadius = 20 } = {}) {
  container.innerHTML = "";
  if (!data.nodes.length) {
    container.innerHTML = '<div class="empty-hint">Estructura vacía</div>';
    return;
  }
  const byId = new Map(data.nodes.map(n => [n.id, n]));
  const maxDepth = Math.max(...data.nodes.map(n => n.depth));
  // Ancho por hojas para evitar solapamientos.
  const leafCount = data.nodes.filter(n => !byId.has(n.id * 2 + 1) && !byId.has(n.id * 2 + 2)).length || 1;
  const width = Math.max(600, leafCount * 70 + 120);
  const rowHeight = 74;
  const height = (maxDepth + 1) * rowHeight + 40;

  // Asignación x por orden de nodo en cada nivel (inorden visual).
  const columns = new Map();
  let columnCursor = 0;
  function assign(nodeId) {
    const node = byId.get(nodeId);
    if (!node) return;
    assign(nodeId * 2 + 1);
    columns.set(nodeId, ++columnCursor);
    assign(nodeId * 2 + 2);
  }
  assign(0);

  const positions = new Map();
  const totalCols = columnCursor || 1;
  data.nodes.forEach(n => {
    positions.set(n.id, {
      x: 40 + (columns.get(n.id) - 1) * (width - 80) / Math.max(1, totalCols - 1 || 1),
      y: 28 + n.depth * rowHeight,
    });
  });

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("width", Math.min(width, 980));

  data.edges.forEach(edge => {
    const a = positions.get(edge.source), b = positions.get(edge.target);
    if (!a || !b) return;
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    line.setAttribute("class", `edge-line ${edge.highlight || ""}`);
    svg.appendChild(line);
  });

  data.nodes.forEach(node => {
    const pos = positions.get(node.id);
    const group = document.createElementNS(svgNS, "g");
    group.dataset.nodeId = node.id;
    group.dataset.value = node.value;
    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("cx", pos.x); circle.setAttribute("cy", pos.y);
    circle.setAttribute("r", nodeRadius);
    circle.setAttribute("class", `node-circle ${node.state || ""}`);
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", pos.x); label.setAttribute("y", pos.y + 4.5);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("class", "node-label");
    label.textContent = node.value;
    group.appendChild(circle); group.appendChild(label);
    if (node.balance !== undefined) { // Badge AVL de factor de equilibrio.
      const badge = document.createElementNS(svgNS, "text");
      badge.setAttribute("x", pos.x + nodeRadius + 4);
      badge.setAttribute("y", pos.y - nodeRadius + 2);
      badge.setAttribute("class", `tree-balance-badge ${Math.abs(node.balance) > 0 ? "" : ""}`);
      badge.textContent = `b${node.balance}`;
      group.appendChild(badge);
    }
    svg.appendChild(group);
  });

  container.appendChild(svg);
}

/* ---------------- Render de grafos (SVG) ----------------
   Disposición circular; los vértices mantienen su orden del
   snapshot para que la demo sea estable entre operaciones.   */
function renderGraphSVG(container, data, highlight = {}) {
  container.innerHTML = "";
  const vertices = data.vertices;
  if (!vertices.length) {
    container.innerHTML = '<div class="empty-hint">Grafo vacío: agregue vértices y aristas</div>';
    return;
  }
  const width = 620, height = 460, radius = Math.min(width, height) / 2 - 60;
  const cx = width / 2, cy = height / 2;
  const positions = new Map();
  vertices.forEach((vertex, i) => {
    const angle = (2 * Math.PI * i) / vertices.length - Math.PI / 2;
    positions.set(vertex, { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) });
  });

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("width", "640");

  const visitedOrder = highlight.order || [];
  data.edges.forEach(edge => {
    const a = positions.get(edge.source), b = positions.get(edge.target);
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    const traversed = visitedOrder.includes(edge.source) && visitedOrder.includes(edge.target);
    line.setAttribute("class", `edge-line ${traversed ? "traversed" : ""}`);
    if (data.directed) {
      const marker = document.createElementNS(svgNS, "polygon");
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      const tipX = b.x - 16 * Math.cos(angle), tipY = b.y - 16 * Math.sin(angle);
      marker.setAttribute("points", `${tipX},${tipY} ${tipX - 9 * Math.cos(angle - .4)},${tipY - 9 * Math.sin(angle - .4)} ${tipX - 9 * Math.cos(angle + .4)},${tipY - 9 * Math.sin(angle + .4)}`);
      marker.setAttribute("class", `edge-arrow ${traversed ? "traversed" : ""}`);
      svg.appendChild(marker);
    }
    if (edge.weight !== undefined && edge.weight !== 1) {
      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", (a.x + b.x) / 2); label.setAttribute("y", (a.y + b.y) / 2 - 4);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "tree-balance-badge");
      label.textContent = edge.weight;
      svg.appendChild(label);
    }
    svg.appendChild(line);
  });

  vertices.forEach(vertex => {
    const pos = positions.get(vertex);
    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("cx", pos.x); circle.setAttribute("cy", pos.y); circle.setAttribute("r", 18);
    const state = visitedOrder.includes(vertex) ? (visitedOrder[visitedOrder.length - 1] === vertex ? "current" : "visited") : "";
    circle.setAttribute("class", `node-circle ${state}`);
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", pos.x); label.setAttribute("y", pos.y + 4.5);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("class", "node-label");
    label.textContent = vertex;
    svg.appendChild(circle); svg.appendChild(label);
  });

  container.appendChild(svg);
}

/* ---------------- Gráficos Chart.js ---------------- */
function makeChart(canvas, config) {
  if (window.Chart && Chart.getCanvas) { /* noop */}
  return new Chart(canvas.getContext("2d"), config);
}
Chart.defaults.color = "#92929E";
Chart.defaults.borderColor = "#25252E";
Chart.defaults.font.family = "Inter, system-ui, sans-serif";
Chart.defaults.font.size = 11;
const CHART_COLORS = ["#8FB4FF", "#4ADE80", "#FACC15", "#F87171", "#C084FC", "#2DD4BF"];

/* ---------------- Controles del reproductor (HTML) ---------------- */
function injectPlayerBar(container, extra = "") {
  container.innerHTML = `
    <div class="player-bar">
      <button class="btn btn-sm" id="playBtn" title="Ejecutar">
        <svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="6,4 20,12 6,20"/></svg> Ejecutar</button>
      <button class="btn btn-sm" id="pauseBtn" title="Pausar">
        <svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="5" y="4" width="5" height="16"/><rect x="14" y="4" width="5" height="16"/></svg> Pausar</button>
      <button class="btn btn-sm" id="stepBtn" title="Paso a paso">
        <svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5,4 15,12 5,20"/><rect x="17" y="4" width="3" height="16"/></svg> Paso</button>
      <button class="btn btn-sm" id="resetBtn" title="Reiniciar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg> Reiniciar</button>
      <div class="speed">
        <span>Velocidad</span>
        <input type="range" id="speedSlider" min="0" max="100" value="55">
      </div>
      ${extra}
      <span class="step-label" id="stepLabel">0 / 0</span>
    </div>`;
}

/* Render de la fila de celdas para arreglos (ordenamiento, búsqueda). */
function renderArrayRow(container, values, highlight = {}) {
  container.innerHTML = "";
  const row = document.createElement("div");
  row.className = "array-row";
  values.forEach((value, i) => {
    const cell = document.createElement("div");
    let cls = "array-cell";
    if (highlight.active?.includes(i)) cls += " cell-active";
    if (highlight.swap?.includes(i)) cls += " cell-swap";
    if (highlight.pivot === i) cls += " cell-pivot";
    if (highlight.done?.includes(i)) cls += " cell-ok";
    if (highlight.dim?.includes(i)) cls += " cell-dim";
    cell.className = cls;
    cell.innerHTML = `${value}<span class="idx">${i}</span>`;
    row.appendChild(cell);
  });
  container.appendChild(row);
}

/* Log de ejecución textual del algoritmo (info técnica en vivo). */
function updateInfoChips(container, chips) {
  container.innerHTML = chips.map(chip =>
    `<div class="info-chip"><div class="k">${chip.k}</div><div class="v ${chip.neutral ? "neutral" : ""}">${chip.v}</div></div>`).join("");
}

function setBigO(container, html) { container.innerHTML = html; }

/* Parser de lista de números desde un input de texto. */
function parseNumberList(text) {
  const values = text.split(/[\s,;]+/).filter(Boolean).map(Number);
  if (values.some(v => Number.isNaN(v))) throw new Error("Todos los valores deben ser numéricos");
  return values;
}

/* ---------------- Sidebar responsive + navegación activa ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  $("#menuToggle")?.addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  const page = document.body.dataset.page;
  $$(".nav-item").forEach(item => {
    const href = item.getAttribute("href");
    if (href === location.pathname || (page && href.endsWith(page))) item.classList.add("active");
  });
});
