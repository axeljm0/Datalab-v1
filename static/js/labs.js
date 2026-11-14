/* ============================================================
   labs.js — lógica de los laboratorios de DataLab
   Cada laboratorio se inicializa según body[data-page].
   Toda operación real proviene de la API REST del backend.
   ============================================================ */
"use strict";

const Labs = {};

/* ============================================================
   DASHBOARD (Módulo A)
   ============================================================ */
Labs.dashboard = async function () {
  try {
    const stats = await API.get("/api/dashboard/stats");
    $("#statRuns").textContent = fmt(stats.runs_recorded);
    $("#statLabs").textContent = stats.laboratories;
    $("#statStructures").textContent = stats.structures;
    $("#statAlgorithms").textContent = stats.algorithms;
    const log = $("#runLog");
    if (stats.recent_runs.length) {
      log.innerHTML = stats.recent_runs.map(run =>
        `<li><span class="mod">${run.module} · ${run.operation}</span>
         <span>${run.details || ""}</span>
         <span class="ms">${run.elapsed_ms !== null ? fmt(run.elapsed_ms) + " ms" : ""}</span></li>`).join("");
    } else {
      log.innerHTML = '<li><span>Aún no hay ejecuciones registradas en esta sesión.</span></li>';
    }
  } catch (error) {
    toast(`No se pudo cargar el dashboard: ${error.message}`, "error");
  }
};

/* ============================================================
   MÓDULO B — LISTAS Y VECTORES
   ============================================================ */
Labs.lists = function () {
  let instanceId = null;
  let structureType = null;

  const typeSelect = $("#listType");
  const valueInput = $("#listValue");
  const indexInput = $("#listIndex");
  const viz = $("#listViz");
  const chips = $("#listChips");

  function draw(snapshot, highlightIndex = -1, hit = false) {
    viz.innerHTML = "";
    if (snapshot.kind === "array") {
      const row = document.createElement("div");
      row.className = "array-row";
      snapshot.elements.forEach((value, i) => {
        const cell = document.createElement("div");
        cell.className = "array-cell" + (i === highlightIndex ? (hit ? " cell-ok" : " cell-active") : "");
        cell.innerHTML = `${value}<span class="idx">${i}</span>`;
        row.appendChild(cell);
      });
      viz.appendChild(row);
      chips.innerHTML = chipsOf([
        ["tamaño", snapshot.size, false], ["capacidad", snapshot.capacity, false],
        ["redimensiones", snapshot.resizes, false], ["tipo", "arreglo dinámico", true],
      ]);
    } else if (snapshot.kind === "matrix") {
      const table = document.createElement("table");
      table.className = "dp-table";
      snapshot.cells.forEach((rowValues, r) => {
        const tr = document.createElement("tr");
        rowValues.forEach((value, c) => {
          const td = document.createElement("td");
          td.textContent = value;
          if (r === highlightIndex?.[0] && c === highlightIndex?.[1]) td.className = "current";
          tr.appendChild(td);
        });
        table.appendChild(tr);
      });
      viz.appendChild(table);
      chips.innerHTML = chipsOf([
        ["filas", snapshot.rows, false], ["columnas", snapshot.cols, false], ["tipo", "matriz", true],
      ]);
    } else {
      // Listas enlazadas: nodos con flechas.
      const row = document.createElement("div");
      row.className = "linked-row";
      if (snapshot.nodes.length === 0) {
        viz.innerHTML = '<div class="empty-hint">Lista vacía: inserte elementos</div>';
        chips.innerHTML = "";
        return;
      }
      row.appendChild(tag("head"));
      snapshot.nodes.forEach((node, i) => {
        const box = document.createElement("div");
        box.className = "linked-node" + (i === highlightIndex ? (hit ? " node-hit" : " node-active") : "");
        const isTail = i === snapshot.nodes.length - 1;
        box.innerHTML = `<span class="val">${node.value}</span>
          ${structureType === "doubly_list" ? '<span class="addr">← prev · next →</span>' : '<span class="addr">next</span>'}`;
        row.appendChild(box);
        const arrow = document.createElement("span");
        arrow.className = "linked-arrow" + (structureType === "doubly_list" ? " dbl" : "");
        arrow.textContent = structureType === "doubly_list" ? "⇄" : "→";
        row.appendChild(arrow);
      });
      row.appendChild(tag("null"));
      viz.appendChild(row);
      chips.innerHTML = chipsOf([
        ["nodos", snapshot.size, false],
        ["recorrido", snapshot.reverse ? `rev: ${snapshot.reverse.slice(0, 4).join(",")}…` : "→", true],
        ["tipo", structureType === "doubly_list" ? "doblemente enlazada" : "simp. enlazada", true],
      ]);
    }
  }

  function tag(text) {
    const span = document.createElement("span");
    span.className = "head-tail-tag";
    span.textContent = text;
    return span;
  }
  function chipsOf(pairs) {
    return pairs.map(([k, v, neutral]) =>
      `<div class="info-chip"><div class="k">${k}</div><div class="v ${neutral ? "neutral" : ""}">${v}</div></div>`).join("");
  }

  async function create() {
    structureType = typeSelect.value;
    const options = {};
    if (structureType === "matrix") {
      options.rows = Number($("#matRows").value);
      options.cols = Number($("#matCols").value);
    }
    const data = await API.post("/api/structures", { type: structureType, options });
    instanceId = data.id;
    draw(data.snapshot);
    toast(`Estructura creada: ${instanceId}`, "ok");
  }

  async function op(operation, extra = {}) {
    if (!instanceId) { toast("Primero cree la estructura", "error"); return; }
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation, ...extra });
      let highlight = -1, hit = false;
      if (data.result && data.result.index !== undefined && data.result.index >= 0) {
        highlight = data.result.index; hit = true;
      }
      draw(data.snapshot, highlight, hit);
      if (data.result) {
        const r = data.result;
        if (r.found === false || r.deleted === false) toast("Elemento no encontrado");
        else if (r.removed !== undefined || r.deleted) toast("Operación aplicada", "ok");
      }
    } catch (error) {
      toast(error.message, "error");
    }
  }

  $("#createListBtn").addEventListener("click", () => create().catch(e => toast(e.message, "error")));
  $("#matConfig").style.display = "none";
  typeSelect.addEventListener("change", () => {
    $("#matConfig").style.display = typeSelect.value === "matrix" ? "flex" : "none";
  });

  // Botones de operación (usan value/index comunes).
  const map = {
    appendBtn: () => op("append", { value: num(valueInput.value) }),
    insertAtBtn: () => op("insert_at", { index: num(indexInput.value), value: num(valueInput.value) }),
    deleteAtBtn: () => op("delete_at", { index: num(indexInput.value) }),
    deleteValBtn: () => op("delete", { value: num(valueInput.value) }),
    searchBtn: () => op("search", { value: num(valueInput.value) }),
    updateBtn: () => op("update", { index: num(indexInput.value), value: num(valueInput.value) }),
    insertHeadBtn: () => op("insert_head", { value: num(valueInput.value) }),
    insertTailBtn: () => op("insert_tail", { value: num(valueInput.value) }),
    traverseBtn: () => op("traverse"),
  };
  Object.entries(map).forEach(([id, fn]) => $(`#${id}`)?.addEventListener("click", () => fn()));
  ["transposeBtn", "fillBtn", "setBtn"].forEach(id => {
    if (!$(`#${id}`)) return;
    $(`#${id}`).addEventListener("click", () => {
      if (id === "transposeBtn") op("transpose");
      if (id === "setBtn") op("set", { row: Number($("#matRow").value), col: Number($("#matCol").value), value: num(valueInput.value) });
      if (id === "fillBtn") op("fill", { values: randomMatrix(Number($("#matRows").value), Number($("#matCols").value)) });
    });
  });

  function num(value) {
    const parsed = Number(value);
    if (Number.isNaN(value) || value === "") throw new Error("Ingrese un valor numérico");
    return parsed;
  }
  function randomMatrix(rows, cols) {
    return Array.from({ length: rows }, () => Array.from({ length: cols }, () => Math.floor(Math.random() * 10)));
  }

  // La matriz usa operaciones específicas: reetiquetar botones.
  create();
};

/* ============================================================
   MÓDULO C — PILAS Y COLAS
   ============================================================ */
Labs.stackQueue = function () {
  let stackId = null, queueId = null;

  async function boot() {
    const s = await API.post("/api/structures", { type: "stack" });
    stackId = s.id; drawStack(s.snapshot);
    const q = await API.post("/api/structures", { type: "queue" });
    queueId = q.id; drawQueue(q.snapshot);
  }

  function itemsView(container, snapshot, topLabel, bottomLabel) {
    container.innerHTML = "";
    if (!snapshot.items.length) {
      container.innerHTML = `<div class="empty-hint">${bottomLabel}</div>`;
      return;
    }
    snapshot.items.forEach((value, i) => {
      const item = document.createElement("div");
      item.className = "stack-item";
      item.textContent = value;
      if (i === snapshot.items.length - 1) item.style.borderColor = "var(--accent)";
      container.appendChild(item);
    });
  }

  function drawStack(snapshot) {
    itemsView($("#stackViz"), snapshot, "cima", "Pila vacía");
    $("#stackChips").innerHTML = `
      <div class="info-chip"><div class="k">elementos</div><div class="v">${snapshot.size}</div></div>
      <div class="info-chip"><div class="k">cima (peek)</div><div class="v">${snapshot.items.at(-1) ?? "—"}</div></div>
      <div class="info-chip"><div class="k">disciplina</div><div class="v neutral">LIFO</div></div>`;
  }

  function drawQueue(snapshot) {
    const container = $("#queueViz");
    container.innerHTML = "";
    if (!snapshot.items.length) {
      container.innerHTML = '<div class="empty-hint">Cola vacía</div>';
    } else {
      container.insertAdjacentHTML("beforeend", '<span class="head-tail-tag">frente</span>');
      snapshot.items.forEach((value, i) => {
        const item = document.createElement("div");
        item.className = "stack-item";
        item.textContent = value;
        if (i === 0) item.style.borderColor = "var(--accent)";
        container.appendChild(item);
      });
      container.insertAdjacentHTML("beforeend", '<span class="head-tail-tag">final</span>');
    }
    $("#queueChips").innerHTML = `
      <div class="info-chip"><div class="k">elementos</div><div class="v">${snapshot.items.length}</div></div>
      <div class="info-chip"><div class="k">frente (front)</div><div class="v">${snapshot.items[0] ?? "—"}</div></div>
      <div class="info-chip"><div class="k">disciplina</div><div class="v neutral">FIFO</div></div>
      <div class="info-chip"><div class="k">redimensiones</div><div class="v">${snapshot.resizes}</div></div>`;
  }

  async function stackOp(operation, value) {
    const data = await API.post(`/api/structures/${stackId}/op`, { operation, value });
    drawStack(data.snapshot);
    if (data.result?.removed !== undefined) toast(`pop() → ${data.result.removed}`, "ok");
    if (data.result?.top !== undefined) toast(`peek() → ${data.result.top}`);
  }
  async function queueOp(operation, value) {
    const data = await API.post(`/api/structures/${queueId}/op`, { operation, value });
    drawQueue(data.snapshot);
    if (data.result?.removed !== undefined) toast(`dequeue() → ${data.result.removed}`, "ok");
    if (data.result?.top !== undefined) toast(`front() → ${data.result.top}`);
  }

  const sq = $("#sqValue");
  const val = () => sq.value === "" ? Math.floor(Math.random() * 99) : Number(sq.value);

  $("#pushBtn").onclick = () => stackOp("push", val()).catch(e => toast(e.message, "error"));
  $("#popBtn").onclick = () => stackOp("pop").catch(e => toast(e.message, "error"));
  $("#peekBtn").onclick = () => stackOp("peek").catch(e => toast(e.message, "error"));
  $("#enqueueBtn").onclick = () => queueOp("enqueue", val()).catch(e => toast(e.message, "error"));
  $("#dequeueBtn").onclick = () => queueOp("dequeue").catch(e => toast(e.message, "error"));
  $("#frontBtn").onclick = () => queueOp("front").catch(e => toast(e.message, "error"));

  /* Demo guiada: historial de operaciones (undo/redo) sobre la pila. */
  $("#historyDemoBtn").onclick = async () => {
    toast("Demo: historial de acciones — cada acción se apila; Ctrl+Z hace pop", "");
    const actions = ["insertar", "formatear", "borrar", "pegar", "deshacer(pop)", "deshacer(pop)"];
    for (const action of actions) {
      await new Promise(r => setTimeout(r, 700));
      if (action.startsWith("deshacer")) await stackOp("pop");
      else await stackOp("push", action);
    }
  };

  /* Demo guiada: gestión de turnos FIFO. */
  $("#turnsDemoBtn").onclick = async () => {
    toast("Demo: atención de turnos — primero en llegar, primero en ser atendido", "");
    const arrivals = ["A-101", "A-102", "A-103"];
    for (const turn of arrivals) { await queueOp("enqueue", turn); await new Promise(r => setTimeout(r, 700)); }
    await queueOp("dequeue");
    await new Promise(r => setTimeout(r, 700));
    await queueOp("enqueue", "A-104");
    await new Promise(r => setTimeout(r, 700));
    await queueOp("dequeue");
  };

  boot().catch(e => toast(e.message, "error"));
};

/* ============================================================
   MÓDULO D — ÁRBOLES Y GRAFOS
   ============================================================ */
Labs.trees = function () {
  let instanceId = null;
  let currentKind = "bst";
  let snapshot = null;
  const viz = $("#treeViz");
  const chips = $("#treeChips");

  async function create(kind, options = {}) {
    currentKind = kind;
    const data = await API.post("/api/structures", { type: kind, options });
    instanceId = data.id;
    snapshot = data.snapshot;
    draw(snapshot);
  }

  function draw(state, visited = []) {
    snapshot = state;
    if (state.kind === "tree") {
      const nodes = state.nodes.map(n => ({
        ...n, state: visited.length ? (visited[visited.length - 1] === n.value ? "current" : visited.includes(n.value) ? "visited" : "") : "",
      }));
      renderTreeSVG(viz, { nodes, edges: state.edges });
      const traversal = state.traversals?.inorder ?? [];
      chips.innerHTML = `
        <div class="info-chip"><div class="k">nodos</div><div class="v">${state.size}</div></div>
        <div class="info-chip"><div class="k">altura</div><div class="v">${state.height}</div></div>
        ${state.variant === "avl" ? `<div class="info-chip"><div class="k">rotaciones</div><div class="v">${state.rotations}</div></div>` : ""}
        <div class="info-chip"><div class="k">inorder</div><div class="v neutral" style="font-size:11px">${traversal.slice(0, 8).join(",")}${traversal.length > 8 ? "…" : ""}</div></div>`;
    } else {
      renderGraphSVG(viz, state, { order: visited });
      chips.innerHTML = `
        <div class="info-chip"><div class="k">vértices</div><div class="v">${state.vertices.length}</div></div>
        <div class="info-chip"><div class="k">aristas</div><div class="v">${state.edges.length}</div></div>
        <div class="info-chip"><div class="k">tipo</div><div class="v neutral">${state.directed ? "dirigido" : "no dirigido"}</div></div>`;
      const adj = $("#adjacencyList");
      adj.innerHTML = Object.entries(state.adjacency).map(([vertex, neighbors]) =>
        `<li><b style="color:var(--accent)">${vertex}</b> → ${neighbors.join(", ") || "sin aristas"}</li>`).join("");
    }
  }

  async function treeOp(operation, extra = {}) {
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation, ...extra });
      draw(data.snapshot);
      const r = data.result || {};
      if (operation === "insert") toast(r.inserted ? `Insertado ${extra.value}` : `${extra.value} ya existía`, r.inserted ? "ok" : "");
      if (operation === "delete") toast(r.deleted ? `Eliminado ${extra.value}` : `${extra.value} no estaba`, r.deleted ? "ok" : "error");
      if (operation === "search") toast(r.found ? `Encontrado en el árbol` : `${extra.value} no existe`, r.found ? "ok" : "error");
    } catch (error) { toast(error.message, "error"); }
  }

  /* Anima un recorrido: frames = prefijos del orden devuelto. */
  async function animateTraversal(operation) {
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation });
      const order = data.result.order;
      const player = new Player({
        frames: order,
        render: (_frame, index) => draw(snapshot, order.slice(0, index + 1)),
        onDone: () => { },
      });
      if (traversalPlayerBound) player.bindControls();
      const label = $("#traversalLabel");
      if (label) label.textContent = `Recorrido ${operation}: ${order.join(" → ")}`;
      player.play();
    } catch (error) { toast(error.message, "error"); }
  }

  $("#createTreeBtn").onclick = () => {
    const kind = $("#treeType").value;
    create(kind).catch(e => toast(e.message, "error"));
  };
  $("#sampleTreeBtn").onclick = async () => {
    await create($("#treeType").value);
    for (const value of [50, 30, 70, 20, 40, 60, 80, 35]) await treeOp("insert", { value });
  };
  $("#resetTreeBtn").onclick = () => create($("#treeType").value).catch(e => toast(e.message, "error"));
  $("#treeInsertBtn").onclick = () => treeOp("insert", { value: Number($("#treeValue").value) });
  $("#treeDeleteBtn").onclick = () => treeOp("delete", { value: Number($("#treeValue").value) });
  $("#treeSearchBtn").onclick = () => treeOp("search", { value: Number($("#treeValue").value) });
  $("#inorderBtn").onclick = () => { bindTraversalPlayer(); animateTraversal("inorder"); };
  $("#preorderBtn").onclick = () => { bindTraversalPlayer(); animateTraversal("preorder"); };
  $("#postorderBtn").onclick = () => { bindTraversalPlayer(); animateTraversal("postorder"); };
  let traversalPlayerBound = false;
  function bindTraversalPlayer() {
    if (traversalPlayerBound) return;
    traversalPlayerBound = true;
    injectPlayerBar($("#traversalPlayer"));
  }

  /* --- Grafo --- */
  $("#graphDirected").onchange = () => create("graph", { directed: $("#graphDirected").checked }).catch(e => toast(e.message, "error"));
  $("#graphAddVertexBtn").onclick = async () => {
    const name = $("#graphVertex").value.trim() || String.fromCharCode(65 + (snapshot?.vertices.length ?? 0));
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation: "add_vertex", source: name });
      draw(data.snapshot); toast(`Vértice ${name} agregado`, "ok");
    } catch (e) { toast(e.message, "error"); }
  };
  $("#graphAddEdgeBtn").onclick = async () => {
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, {
        operation: "add_edge",
        source: $("#graphFrom").value.trim(), target: $("#graphTo").value.trim(),
      });
      draw(data.snapshot); toast("Arista agregada", "ok");
    } catch (e) { toast(e.message, "error"); }
  };
  $("#graphSampleBtn").onclick = async () => {
    await create("graph", { directed: $("#graphDirected").checked });
    for (const vertex of ["A", "B", "C", "D", "E", "F"]) await API.post(`/api/structures/${instanceId}/op`, { operation: "add_vertex", source: vertex });
    for (const [a, b] of [["A", "B"], ["A", "C"], ["B", "D"], ["C", "E"], ["D", "F"], ["E", "F"]]) {
      await API.post(`/api/structures/${instanceId}/op`, { operation: "add_edge", source: a, target: b });
    }
  };
  $("#graphBfsBtn").onclick = async () => {
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation: "bfs", source: $("#graphStart").value.trim() });
      const order = data.result.order;
      const player = new Player({ frames: order, render: (_f, i) => draw(snapshot, order.slice(0, i + 1)) });
      player.bindControls();
      $("#traversalLabel").textContent = `BFS desde ${order[0]}: ${order.join(" → ")}`;
      player.play();
    } catch (e) { toast(e.message, "error"); }
  };
  $("#graphDfsBtn").onclick = async () => {
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation: "dfs", source: $("#graphStart").value.trim() });
      const order = data.result.order;
      const player = new Player({ frames: order, render: (_f, i) => draw(snapshot, order.slice(0, i + 1)) });
      player.bindControls();
      $("#traversalLabel").textContent = `DFS desde ${order[0]}: ${order.join(" → ")}`;
      player.play();
    } catch (e) { toast(e.message, "error"); }
  };

  create("bst").catch(e => toast(e.message, "error"));
};

/* ============================================================
   MÓDULO E — BÚSQUEDA Y ORDENAMIENTO
   ============================================================ */
Labs.searchSort = function () {
  const viz = $("#ssViz");
  const chips = $("#ssChips");
  const bigO = $("#ssBigO");
  const input = $("#ssInput");

  let lastSearchSteps = null; // {values, steps}
  injectPlayerBar($("#playerHolder"));

  $("#ssRandomBtn").onclick = () => {
    const n = Number($("#ssCount").value) || 15;
    const values = Array.from({ length: n }, () => Math.floor(Math.random() * 200) - 100);
    input.value = values.join(", ");
    drawArray(values, {});
  };

  function getValues() {
    try {
      const values = parseNumberList(input.value);
      if (!values.length) throw new Error("Ingrese al menos un valor");
      if (values.length > 300) throw new Error("Máximo 300 valores para la animación");
      return values;
    } catch (error) { toast(error.message, "error"); return null; }
  }

  function drawArray(values, highlight) {
    renderArrayRow(viz, values, highlight);
  }

  function drawStatic() {
    const values = parseOrNull(input.value);
    if (values && values.length && values.length <= 300) drawArray(values, {});
  }
  function parseOrNull(text) {
    try { return parseNumberList(text); } catch { return null; }
  }

  /* --- Búsqueda --- */
  $("#searchRunBtn").onclick = async () => {
    const values = getValues(); if (!values) return;
    const target = Number($("#ssTarget").value);
    if (Number.isNaN(target)) { toast("Ingrese el objetivo (target)", "error"); return; }
    const algorithm = $("#searchType").value;
    try {
      const data = await API.post(`/api/search/${algorithm}`, { values, target });
      lastSearchSteps = { values, steps: data.steps };
      const frames = data.steps.map(step => step);
      const player = new Player({
        frames,
        render: (frame) => {
          const highlight = { active: [frame.index ?? frame.middle] };
          if (frame.match) highlight.done = [frame.index ?? frame.middle];
          if (algorithm === "binary") {
            highlight.dim = values.map((_, i) => i).filter(i => i < frame.low || i > frame.high);
          }
          drawArray(values, highlight);
          updateInfoChips(chips, [
            { k: "algoritmo", v: algorithm === "binary" ? "Binary Search" : "Linear Search", neutral: true },
            { k: "comparaciones", v: frame.comparison },
            { k: "índice actual", v: frame.index ?? frame.middle },
            algorithm === "binary" ? { k: "rango [low, high]", v: `${frame.low}..${frame.high}` } : { k: "valor", v: frame.value, neutral: true },
          ]);
        },
        onDone: () => {
          const found = data.found;
          setBigO(bigO, `
            <b>Resultado:</b> ${found ? `el valor ${target} está en el índice ${data.index}` : `el valor ${target} no está en la lista`} ·
            <b>${data.comparisons}</b> comparaciones · <b>${fmt(data.time_ms ?? data.search_time_ms, 4)} ms</b><br>
            <b>Complejidad:</b> mejor ${data.complexity.best} · promedio ${data.complexity.average} · peor ${data.complexity.worst} · espacio ${data.complexity.space}`);
        },
      });
      player.bindControls();
      player.play();
      if (!data.found) toast("El valor no está en la lista");
      if (data.prep_note) toast(data.prep_note, "ok");
    } catch (error) {
      toast(error.message, "error");
      if (error.payload?.data?.prep_hint) {
        setBigO(bigO, `<b>Precondición incumplida:</b> ${error.payload.data.prep_hint}`);
      }
      drawArray(values, {});
    }
  };

  /* --- Ordenamiento --- */
  $("#sortRunBtn").onclick = async () => {
    const values = getValues(); if (!values) return;
    const algorithm = $("#sortType").value;
    try {
      const data = await API.post(`/api/sort/${algorithm}`, { values });
      if (!data.steps.length) {
        toast("Conjunto demasiado grande para animación: se muestran los resultados", "ok");
        drawArray(data.sorted, { done: data.sorted.map((_, i) => i) });
        return;
      }
      const player = new Player({
        frames: data.steps,
        render: (frame) => {
          drawArray(frame.array, {
            active: frame.type === "compare" ? frame.indices : [],
            swap: frame.type === "swap" ? frame.indices : [],
            pivot: frame.type === "pivot" ? frame.indices[0] : undefined,
          });
          updateInfoChips(chips, [
            { k: "algoritmo", v: data.info.name, neutral: true },
            { k: "comparaciones", v: countComps(data, frame) },
            { k: "intercambios", v: countSwaps(data, frame) },
            { k: "acción", v: frame.type, neutral: true },
          ]);
        },
        onDone: () => {
          setBigO(bigO, `<b>${data.info.name}:</b> ${data.info.description}<br>
            <b>Resultado:</b> ${data.comparisons} comparaciones · ${data.swaps} intercambios · ${fmt(data.time_ms, 4)} ms<br>
            <b>Complejidad:</b> mejor ${data.info.best} · promedio ${data.info.average} · peor ${data.info.worst} · espacio ${data.info.space} · estable: ${data.info.stable ? "sí" : "no"}`);
        },
      });
      player.bindControls();
      player.play();
    } catch (error) { toast(error.message, "error"); }
  };

  function countComps(data, frame) {
    // Recuenta pasos hasta el frame actual (comparaciones acumuladas).
    let count = 0;
    for (let i = 0; i <= data.steps.indexOf(frame); i++) {
      if (["compare", "pivot"].includes(data.steps[i].type)) count++;
    }
    return count;
  }
  function countSwaps(data, frame) {
    let count = 0;
    for (let i = 0; i <= data.steps.indexOf(frame); i++) {
      if (data.steps[i].type === "swap") count++;
    }
    return count;
  }

  /* --- Comparación --- */
  let compareChart = null;
  $("#compareBtn").onclick = async () => {
    const values = getValues(); if (!values) return;
    const algorithms = ["bubble", "selection", "quick"].filter(name => $(`#chk_${name}`).checked);
    if (!algorithms.length) { toast("Seleccione al menos un algoritmo", "error"); return; }
    try {
      const data = await API.post("/api/sort/compare", { values, algorithms });
      const table = $("#compareTable");
      table.innerHTML = `<tr><th>Algoritmo</th><th>Comparaciones</th><th>Intercambios</th><th>Tiempo (ms)</th><th>Correcto</th></tr>` +
        data.results.map(r => `<tr><td style="color:var(--text)">${r.info.name}</td><td>${fmt(r.comparisons)}</td><td>${fmt(r.swaps)}</td><td>${fmt(r.time_ms, 4)}</td><td style="color:var(--ok)">${r.correct ? "sí" : "NO"}</td></tr>`).join("");
      if (compareChart) compareChart.destroy();
      compareChart = makeChart($("#compareChart"), {
        type: "bar",
        data: {
          labels: data.results.map(r => r.info.name),
          datasets: [
            { label: "Comparaciones", data: data.results.map(r => r.comparisons), backgroundColor: CHART_COLORS[0] },
            { label: "Intercambios", data: data.results.map(r => r.swaps), backgroundColor: CHART_COLORS[2] },
          ],
        },
        options: { scales: { y: { beginAtZero: true } }, plugins: { title: { display: true, text: `Comparación con n=${data.size} elementos` } } },
      });
      setBigO(bigO, `<b>Observación académica:</b> con datos aleatorios Bubble y Selection crecen cuadráticamente
        (≈ n²/2 comparaciones) mientras Quick Sort crece como n·log n. Cambie el tamaño y observe la razón de crecimiento.`);
    } catch (error) { toast(error.message, "error"); }
  };

  drawStatic();
};

/* ============================================================
   MÓDULO F — TABLAS HASH
   ============================================================ */
Labs.hash = function () {
  let instanceId = null;

  function draw(snapshot, highlightKey = null) {
    const buckets = $("#hashBuckets");
    buckets.innerHTML = "";
    snapshot.buckets.forEach(bucket => {
      const row = document.createElement("div");
      row.className = "hash-bucket";
      const hasChain = bucket.pairs.length > 1;
      row.innerHTML = `<span class="bucket-index">[${bucket.index}]</span><div class="bucket-chain">${
        bucket.pairs.length === 0 ? '<span class="null-tag">vacío</span>' :
        bucket.pairs.map(pair => {
          const highlight = highlightKey !== null && pair.key === highlightKey;
          return `<span class="hash-pair ${highlight ? "highlight" : ""} ${hasChain ? "chain" : ""}">
            <span class="k">${pair.key}</span><span class="v">=</span><span class="v">${pair.value}</span>
            ${hasChain ? '<span class="v">⛓</span>' : ""}</span>`;
        }).join("")}</div>`;
      buckets.appendChild(row);
    });
    const pct = Math.min(100, snapshot.load_factor * 100);
    $("#loadFill").style.width = `${pct}%`;
    $("#loadFill").className = `load-fill ${snapshot.load_factor > snapshot.load_limit ? "over" : ""}`;
    $("#hashChips").innerHTML = `
      <div class="info-chip"><div class="k">elementos</div><div class="v">${snapshot.size}</div></div>
      <div class="info-chip"><div class="k">capacidad</div><div class="v">${snapshot.capacity}</div></div>
      <div class="info-chip"><div class="k">factor de carga</div><div class="v">${snapshot.load_factor} / ${snapshot.load_limit}</div></div>
      <div class="info-chip"><div class="k">colisiones</div><div class="v">${snapshot.collisions}</div></div>
      <div class="info-chip"><div class="k">redimensiones</div><div class="v">${snapshot.resizes}</div></div>`;
  }

  async function op(operation, payload) {
    if (!instanceId) return;
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation, ...payload });
      draw(data.snapshot, payload.key);
      if (data.result) {
        const r = data.result;
        if (operation === "search") toast(`Búsqueda O(1): valor = ${r.value}`, "ok");
        if (operation === "remove") toast(`Clave eliminada (valor ${r.value})`, "ok");
        if (operation === "insert") toast(r.updated ? "Clave existente: valor actualizado" : "Clave insertada", "ok");
      }
    } catch (error) {
      toast(error.message, "error");
      API.get(`/api/structures/${instanceId}`).then(s => draw(s)).catch(() => {});
    }
  }

  async function create() {
    const capacity = Number($("#hashCapacity").value) || 8;
    const data = await API.post("/api/structures", { type: "hash_table", options: { capacity } });
    instanceId = data.id;
    draw(data.snapshot);
  }
  $("#hashCreateBtn").onclick = () => create().catch(e => toast(e.message, "error"));
  $("#hashInsertBtn").onclick = () => op("insert", { key: $("#hashKey").value, value: $("#hashValue").value });
  $("#hashSearchBtn").onclick = () => op("search", { key: $("#hashKey").value });
  $("#hashRemoveBtn").onclick = () => op("remove", { key: $("#hashKey").value });
  $("#hashDemoBtn").onclick = async () => {
    await create();
    const sample = [["ana", 25], ["luis", 31], ["maria", 19], ["pedro", 42], ["ana2", 27], ["sofia", 23], ["carla", 29], ["juan", 35], ["eva", 22], ["raul", 48]];
    for (const [key, value] of sample) {
      await op("insert", { key, value });
      await new Promise(r => setTimeout(r, 350));
    }
    toast("Demostración: observe los buckets con colisiones (⛓) y el factor de carga", "ok");
  };
  create().catch(e => toast(e.message, "error"));
};

/* ============================================================
   MÓDULO G — PROGRAMACIÓN DINÁMICA
   ============================================================ */
Labs.dynamic = function () {
  let player = null;
  injectPlayerBar($("#playerHolder"));

  function bindPlayer(frames, render) {
    if (player) player.pause();
    player = new Player({ frames, render });
    player.bindControls();
    player.play();
  }

  /* --- Fibonacci --- */
  $("#fibRunBtn").onclick = async () => {
    try {
      const n = Number($("#fibN").value);
      const data = await API.post("/api/dp/fibonacci", { n });
      const table = $("#dpTableBox");
      table.innerHTML = data.dynamic.table.length
        ? `<table class="dp-table"><tr><th>f(i)</th>${data.dynamic.table.map((_, i) => `<th>${i}</th>`).join("")}</tr>
           <tr><th>valor</th>${data.dynamic.table.map(v => `<td>${v}</td>`).join("")}</tr></table>`
        : `<table class="dp-table"><tr><th>f(0)</th><td>0</td></tr></table>`;
      const cells = $$("td", table);
      bindPlayer(data.dynamic.table.map((v, i) => i),
        (_f, i) => { cells.forEach((c, j) => c.classList.toggle("current", j === i)); });
      const recursive = data.recursive;
      $("#dpResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">f(${n}) dinámico</div><div class="v">${data.dynamic.value}</div></div>
          <div class="info-chip"><div class="k">llamadas dinámico</div><div class="v">${data.dynamic.calls}</div></div>
          <div class="info-chip"><div class="k">llamadas recursivo</div><div class="v">${recursive ? recursive.calls : "&gt; 2^25"}</div></div>
          <div class="info-chip"><div class="k">tiempo DP</div><div class="v">${fmt(data.dynamic.time_ms, 5)} ms</div></div>
        </div>
        <div class="big-o"><b>Recursivo puro:</b> O(2^n) tiempo — recalcula los mismos subproblemas millones de veces.<br>
        <b>Dinámico (tabulación):</b> O(n) tiempo, O(n) espacio — cada subproblema se resuelve una vez.<br>
        <b>Conclusión:</b> ${data.conclusion}</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  /* --- Mochila 0/1 --- */
  $("#knapRunBtn").onclick = async () => {
    try {
      const weights = parseNumberList($("#knapWeights").value);
      const values = parseNumberList($("#knapValues").value);
      const capacity = Number($("#knapCapacity").value);
      if (weights.length !== values.length) throw new Error("Pesos y valores deben tener la misma cantidad");
      const data = await API.post("/api/dp/knapsack", { weights, values, capacity });
      const box = $("#dpTableBox");
      const rows = data.table.length, cols = data.table[0].length;
      let html = `<table class="dp-table"><tr><th>dp[i][w]</th>${Array.from({ length: cols }, (_, w) => `<th>${w}</th>`).join("")}</tr>`;
      data.table.forEach((row, i) => {
        html += `<tr><th>${i === 0 ? "∅" : `obj ${i - 1}`}</th>${row.map(v => `<td>${v}</td>`).join("")}</tr>`;
      });
      html += "</table>";
      box.innerHTML = html;
      const selectedCells = new Set(data.selected_items.map(item => `${item + 1}`));
      const stepMap = new Map(data.steps.map(s => [`${s.i}:${s.w}`, s]));
      bindPlayer(data.steps.map((s, i) => i), (_f, frameIndex) => {
        const processed = data.steps.slice(0, frameIndex + 1);
        $("td", box) && $$("td", box).forEach(td => td.classList.remove("current"));
        processed.forEach(step => {
          const cell = box.rows[step.i]?.cells[step.w + 1];
          if (cell) cell.classList.add("filled");
        });
        const current = data.steps[frameIndex];
        const cell = box.rows[current.i]?.cells[current.w + 1];
        if (cell) cell.classList.add("current");
      });
      $("#dpResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">valor óptimo</div><div class="v">${data.best_value}</div></div>
          <div class="info-chip"><div class="k">objetos elegidos</div><div class="v neutral">${data.selected_items.map(i => `#${i} (p=${weights[i]}, v=${values[i]})`).join(", ") || "ninguno"}</div></div>
          <div class="info-chip"><div class="k">tiempo</div><div class="v">${fmt(data.time_ms, 4)} ms</div></div>
        </div>
        <div class="big-o"><b>Estado:</b> dp[i][w] = mejor valor usando los primeros i objetos con capacidad w.<br>
        <b>Transición:</b> dp[i][w] = max(dp[i-1][w], dp[i-1][w-peso_i] + valor_i).<br>
        <b>Complejidad:</b> O(n·W) tiempo y espacio. La reconstrucción recorre la tabla hacia atrás para identificar los objetos elegidos.</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  /* --- Coin Change --- */
  $("#coinRunBtn").onclick = async () => {
    try {
      const coins = parseNumberList($("#coinDenoms").value);
      const amount = Number($("#coinAmount").value);
      const data = await API.post("/api/dp/coin-change", { coins, amount });
      const box = $("#dpTableBox");
      let html = `<table class="dp-table"><tr><th>monto a</th>${data.table.map((_, i) => `<th>${i}</th>`).join("")}</tr><tr><th>dp[a]</th>`;
      html += data.table.map(v => `<td>${v > amount ? "∞" : v}</td>`).join("") + "</tr></table>";
      box.innerHTML = html;
      bindPlayer(data.table.map((v, i) => i), (_f, i) => {
        $$("td", box).forEach((td, j) => {
          td.classList.remove("current", "filled");
          if (j < i) td.classList.add("filled");
          if (j === i) td.classList.add("current");
        });
      });
      $("#dpResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">mínimo de monedas</div><div class="v">${data.solvable ? data.min_coins : "imposible"}</div></div>
          <div class="info-chip"><div class="k">monedas usadas</div><div class="v neutral">${data.coins_used.join(" + ") || "—"}</div></div>
        </div>
        <div class="big-o"><b>Estado:</b> dp[a] = mínimo de monedas para el monto a.<br>
        <b>Transición:</b> dp[a] = min(dp[a - moneda] + 1) para cada moneda ≤ a.<br>
        <b>Complejidad:</b> O(monto·n) tiempo, O(monto) espacio.</div>`;
    } catch (error) { toast(error.message, "error"); }
  };
};

/* ============================================================
   MÓDULO H — GREEDY
   ============================================================ */
Labs.greedy = function () {
  let player = null;
  injectPlayerBar($("#greedyPlayer"));
  function bindPlayer(frames, render) {
    if (player) player.pause();
    player = new Player({ frames, render });
    player.bindControls();
    player.play();
  }

  function renderActivities(container, decisions) {
    container.innerHTML = '<div class="greedy-track">' + decisions.map((d, i) => `
      <div class="greedy-item ${d.chosen ? "chosen" : "rejected"}" data-i="${i}">
        <span class="tag">act ${d.activity.id}</span>
        <div class="greedy-bar" style="margin-left:${d.activity.start * 3}%; width:${(d.activity.end - d.activity.start) * 3}%">${d.activity.start} → ${d.activity.end}</div>
      </div>`).join("") + "</div>";
  }

  $("#activitySampleBtn").onclick = () => {
    $("#activityInput").value = "1,3\n2,5\n4,7\n1,8\n5,9\n8,10\n3,4";
  };
  $("#activityRunBtn").onclick = async () => {
    try {
      const activities = $("#activityInput").value.trim().split("\n").map((line, i) => {
        const [start, end] = line.split(",").map(Number);
        if (Number.isNaN(start) || Number.isNaN(end)) throw new Error("Formato: start,end por línea");
        return { id: i + 1, start, end };
      });
      const data = await API.post("/api/greedy/activities", { activities });
      const container = $("#greedyViz");
      renderActivities(container, data.decisions);
      bindPlayer(data.decisions.map((d, i) => i), (_f, i) => {
        $$(".greedy-item", container).forEach((el, j) => {
          el.style.visibility = j <= i ? "visible" : "hidden";
          if (j === i) el.style.transform = "scale(1.02)";
        });
      });
      $("#greedyResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">actividades elegidas</div><div class="v">${data.count}</div></div>
          <div class="info-chip"><div class="k">¿solución óptima?</div><div class="v" style="color:var(--ok)">sí — garantizada</div></div>
        </div>
        <div class="big-o"><b>Estrategia:</b> ${data.strategy}.<br>
        <b>Por qué es óptima:</b> escoger la actividad que termina primero nunca impide una solución mejor:
        si existe una solución óptima, su primera actividad puede reemplazarse por la de menor fin sin perder elementos.<br>
        <b>Complejidad:</b> ${data.complexity.time}.<br>
        <b>Decisiones:</b> ${data.decisions.map(d => `<br>· act ${d.activity.id} [${d.activity.start},${d.activity.end}] → ${d.chosen ? "elegida" : "descartada"}: ${d.reason}`).join("")}</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#coinSampleBtn").onclick = () => {
    $("#greedyDenoms").value = "1, 2, 5, 10, 20, 50, 100";
    $("#greedyAmount").value = "289";
  };
  $("#coinNonCanonicalBtn").onclick = () => {
    $("#greedyDenoms").value = "1, 3, 4";
    $("#greedyAmount").value = "6";
  };
  $("#greedyCoinRunBtn").onclick = async () => {
    try {
      const denominations = parseNumberList($("#greedyDenoms").value);
      const amount = Number($("#greedyAmount").value);
      const data = await API.post("/api/greedy/coins", { denominations, amount });
      const optimalBadge = data.optimal === true
        ? '<span style="color:var(--ok)">sistema canónico: greedy garantiza el óptimo</span>'
        : data.optimal === false
          ? '<span style="color:var(--warn)">sistema NO canónico: greedy NO garantiza el óptimo</span>'
          : '<span>sin verificación</span>';
      $("#greedyResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">monedas greedy</div><div class="v">${data.solvable ? data.total_coins : "imposible"}</div></div>
          <div class="info-chip"><div class="k">mínimo real (DP)</div><div class="v">${data.dp_min_coins ?? "—"}</div></div>
        </div>
        <div class="big-o"><b>Monedas usadas:</b> ${data.coins_used.join(" + ") || "—"}<br>
        <b>Estrategia:</b> ${data.strategy}<br><b>¿Óptimo garantizado?</b> ${optimalBadge}<br>
        ${data.optimal === false ? "<b>Análisis:</b> este sistema demuestra el riesgo de greedy: la elección local (moneda mayor) conduce a 4+1+1, pero el óptimo global es 3+3. Con sistemas canónicos (1,2,5,10…) la elección voraz sí es segura." : ""}</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#canonicalCheckBtn").onclick = async () => {
    try {
      const denominations = parseNumberList($("#greedyDenoms").value);
      const data = await API.post("/api/greedy/canonical-check", { denominations });
      $("#greedyResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">sistema</div><div class="v neutral">${denominations.join(",")}</div></div>
          <div class="info-chip"><div class="k">¿canónico?</div><div class="v" style="color:${data.canonical ? "var(--ok)" : "var(--warn)"}">${data.canonical ? "sí" : "no"}</div></div>
        </div>
        <div class="big-o"><b>Verificación:</b> se comparó greedy contra programación dinámica para cada monto hasta ${data.checked_up_to}.
        ${data.counterexamples.length ? `<b>Contraejemplos:</b> ${data.counterexamples.map(c => `monto ${c.amount}: greedy=${c.greedy}, óptimo=${c.optimal}`).join(" · ")}` : "No se encontraron contraejemplos: greedy es óptimo para este sistema."}</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#intervalRunBtn").onclick = async () => {
    try {
      const intervals = $("#intervalInput").value.trim().split("\n").map((line, i) => {
        const [start, end] = line.split(",").map(Number);
        if (Number.isNaN(start) || Number.isNaN(end)) throw new Error("Formato: inicio,fin por línea");
        return { id: i + 1, start, end };
      });
      const data = await API.post("/api/greedy/intervals", { intervals });
      renderActivities($("#greedyViz"), data.decisions);
      bindPlayer(data.decisions.map((d, i) => i), (_f, i) => {
        $$(".greedy-item").forEach((el, j) => el.style.visibility = j <= i ? "visible" : "hidden");
      });
      $("#greedyResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">intervalos compatibles</div><div class="v">${data.count}</div></div>
        </div>
        <div class="big-o"><b>Estrategia:</b> ${data.strategy}.<br>
        <b>Nota:</b> intervalos que se tocan en un extremo (fin = inicio del siguiente) NO se solapan.</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#activitySampleBtn").click();
  $("#coinSampleBtn").click();
};

/* ============================================================
   MÓDULO I — ESTRUCTURAS AVANZADAS
   ============================================================ */
Labs.advanced = function () {
  let instanceId = null;
  const viz = $("#advViz");
  const chips = $("#advChips");

  function draw(snapshot) {
    if (snapshot.kind === "heap") {
      const nodes = [], edges = [];
      let index = 0;
      snapshot.levels.forEach((level, depth) => {
        level.forEach((value, offsetInLevel) => {
          const id = index++;
          nodes.push({ id, value, depth, state: snapshot.highlight === value ? "hit" : "" });
          if (id > 0) edges.push({ source: Math.floor((id - 1) / 2), target: id });
        });
      });
      renderTreeSVG(viz, { nodes, edges }, { nodeRadius: 18 });
      chips.innerHTML = `
        <div class="info-chip"><div class="k">tipo</div><div class="v neutral">${snapshot.variant === "min" ? "Min Heap" : "Max Heap"}</div></div>
        <div class="info-chip"><div class="k">elementos</div><div class="v">${snapshot.size}</div></div>
        <div class="info-chip"><div class="k">raíz (${snapshot.variant === "min" ? "mínimo" : "máximo"})</div><div class="v">${snapshot.items[0] ?? "—"}</div></div>
        <div class="info-chip"><div class="k">movimientos sift</div><div class="v">${snapshot.swaps}</div></div>
        <div class="info-chip"><div class="k">comparaciones</div><div class="v">${snapshot.comparisons}</div></div>`;
    } else if (snapshot.kind === "b_tree") {
      drawBTree(viz, snapshot);
      chips.innerHTML = `
        <div class="info-chip"><div class="k">claves</div><div class="v">${snapshot.size}</div></div>
        <div class="info-chip"><div class="k">grado mínimo t</div><div class="v">${snapshot.min_degree}</div></div>
        <div class="info-chip"><div class="k">altura</div><div class="v">${snapshot.height}</div></div>
        <div class="info-chip"><div class="k">divisiones de nodo</div><div class="v">${snapshot.splits}</div></div>
        <div class="info-chip"><div class="k">máx claves/nodo</div><div class="v neutral">${2 * snapshot.min_degree - 1}</div></div>`;
    } else { // avl / bst
      renderTreeSVG(viz, snapshot);
      chips.innerHTML = `
        <div class="info-chip"><div class="k">nodos</div><div class="v">${snapshot.size}</div></div>
        <div class="info-chip"><div class="k">altura</div><div class="v">${snapshot.height}</div></div>
        <div class="info-chip"><div class="k">rotaciones</div><div class="v">${snapshot.rotations ?? 0}</div></div>
        <div class="info-chip"><div class="k">altura teórica log₂n</div><div class="v">${Math.ceil(Math.log2(snapshot.size + 1))}</div></div>`;
    }
  }

  /* Árbol B: cajas con claves ordenadas dentro de cada nodo. */
  function drawBTree(container, snapshot) {
    container.innerHTML = "";
    if (!snapshot.nodes.length) { container.innerHTML = '<div class="empty-hint">Árbol B vacío</div>'; return; }
    const byId = new Map(snapshot.nodes.map(n => [n.id, n]));
    const maxDepth = Math.max(...snapshot.nodes.map(n => n.depth));
    const rowHeight = 86;
    const leaves = snapshot.nodes.filter(n => n.leaf).length || 1;
    const width = Math.max(640, leaves * 90);
    const height = (maxDepth + 1) * rowHeight + 30;
    const columns = new Map();
    let cursor = 0;
    function assign(id) {
      const node = byId.get(id); if (!node) return;
      node.children_order = snapshot.edges.filter(e => e.source === id).map(e => e.target);
      node.children_order.forEach(assign);
      columns.set(id, ++cursor);
    }
    assign(0);
    const totalCols = cursor;
    const positions = new Map();
    snapshot.nodes.forEach(n => {
      positions.set(n.id, { x: 60 + (columns.get(n.id) - 1) * (width - 120) / Math.max(1, totalCols - 1), y: 26 + n.depth * rowHeight });
    });
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", Math.min(width, 960));
    snapshot.edges.forEach(edge => {
      const a = positions.get(edge.source), b = positions.get(edge.target);
      if (!a || !b) return;
      const line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", a.x); line.setAttribute("y1", a.y + 18);
      line.setAttribute("x2", b.x); line.setAttribute("y2", b.y - 18);
      line.setAttribute("class", "edge-line");
      svg.appendChild(line);
    });
    snapshot.nodes.forEach(node => {
      const pos = positions.get(node.id);
      const w = Math.max(46, node.keys.length * 26 + 12);
      const rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("x", pos.x - w / 2); rect.setAttribute("y", pos.y - 18);
      rect.setAttribute("width", w); rect.setAttribute("height", 36);
      rect.setAttribute("rx", 7);
      rect.setAttribute("fill", node.leaf ? "#1a2338" : "#232733");
      rect.setAttribute("stroke", "#8FB4FF66");
      svg.appendChild(rect);
      node.keys.forEach((key, i) => {
        const text = document.createElementNS(svgNS, "text");
        text.setAttribute("x", pos.x - w / 2 + 12 + i * 26);
        text.setAttribute("y", pos.y + 4.5);
        text.setAttribute("class", "node-label");
        text.setAttribute("font-size", "12");
        text.textContent = key;
        svg.appendChild(text);
      });
    });
    container.appendChild(svg);
  }

  async function op(operation, payload = {}) {
    if (!instanceId) return;
    try {
      const data = await API.post(`/api/structures/${instanceId}/op`, { operation, ...payload });
      draw(data.snapshot);
      const r = data.result;
      if (r && operation === "pop") toast(`pop() → ${r.removed}`, "ok");
      if (r && operation === "peek") toast(`peek() → ${r.top}`);
      if (r && "inserted" in r) toast(r.inserted ? `Insertado ${payload.value}` : `${payload.value} ya existía`, r.inserted ? "ok" : "");
      if (r && "deleted" in r) toast(r.deleted ? `Eliminado ${payload.value}` : `${payload.value} no estaba`, r.deleted ? "ok" : "error");
      if (r && "found" in r) toast(r.found ? "Encontrado" : "No existe", r.found ? "ok" : "error");
    } catch (error) { toast(error.message, "error"); }
  }

  async function create(kind, options = {}) {
    const data = await API.post("/api/structures", { type: kind, options });
    instanceId = data.id;
    draw(data.snapshot);
  }

  $("#advType").onchange = () => {
    const kind = $("#advType").value;
    const options = kind === "b_tree" ? { min_degree: Number($("#advDegree").value) || 2 } : {};
    $("#advDegree").parentElement.style.visibility = kind === "b_tree" ? "visible" : "hidden";
    create(kind, options).catch(e => toast(e.message, "error"));
  };
  $("#advInsertBtn").onclick = () => {
    const kind = $("#advType").value;
    const value = Number($("#advValue").value);
    op("push", { value }).then(() => { if (kind !== "min_heap" && kind !== "max_heap") op("insert", { value }); });
  };
  $("#advRemoveBtn").onclick = () => {
    const kind = $("#advType").value;
    if (kind === "min_heap" || kind === "max_heap") op("pop");
    else op("delete", { value: Number($("#advValue").value) });
  };
  $("#advPeekBtn").onclick = () => {
    const kind = $("#advType").value;
    if (kind === "min_heap" || kind === "max_heap") op("peek");
    else op("search", { value: Number($("#advValue").value) });
  };
  $("#advHeapSortBtn").onclick = async () => {
    // Demostración: heapsort extrae de forma ordenada usando pops repetidos.
    const kind = $("#advType").value;
    if (kind !== "min_heap" && kind !== "max_heap") { toast("Seleccione un heap para esta demo", "error"); return; }
    toast("Heapsort: repetir pop() extrae los elementos en orden", "");
    for (let i = 0; i < 4; i++) { await op("pop"); await new Promise(r => setTimeout(r, 500)); }
  };
  $("#advSampleBtn").onclick = async () => {
    const kind = $("#advType").value;
    await create(kind, kind === "b_tree" ? { min_degree: Number($("#advDegree").value) || 2 } : {});
    const values = kind === "b_tree" ? [10, 20, 5, 6, 12, 30, 7, 17, 3, 25, 40, 1] : [50, 30, 70, 20, 40, 60, 80, 10];
    for (const value of values) {
      const isHeap = kind === "min_heap" || kind === "max_heap";
      await API.post(`/api/structures/${instanceId}/op`, { operation: isHeap ? "push" : "insert", value });
      const snap = await API.get(`/api/structures/${instanceId}`);
      draw(snap);
      await new Promise(r => setTimeout(r, 260));
    }
  };
  $("#advResetBtn").onclick = () => $("#advType").dispatchEvent(new Event("change"));
  create("min_heap").catch(e => toast(e.message, "error"));
};

/* ============================================================
   MÓDULO J — CIENCIA DE DATOS
   ============================================================ */
Labs.data = function () {
  let currentDataset = null;
  let resultRows = null;
  let currentColumns = [];

  function renderTable(container, columns, rows, total) {
    if (!rows.length) { container.innerHTML = '<div class="empty-hint">Sin filas para mostrar</div>'; return; }
    container.innerHTML = `<table class="data-table"><thead><tr>${columns.map(c => `<th>${c}</th>`).join("")}</tr></thead>
      <tbody>${rows.slice(0, 50).map(row => `<tr>${row.map(v => `<td>${v}</td>`).join("")}</tr>`).join("")}</tbody></table>
      <p class="explain">Mostrando ${Math.min(50, rows.length)} de ${total ?? rows.length} filas</p>`;
  }

  async function refresh() {
    const datasets = await API.get("/api/datasets");
    const select = $("#datasetSelect");
    select.innerHTML = datasets.length
      ? datasets.map(d => `<option value="${d.name}">${d.name} (${d.count} filas)</option>`).join("")
      : '<option value="">— sin datasets —</option>';
    if (datasets.length) {
      currentDataset = datasets[datasets.length - 1].name;
      select.value = currentDataset;
      await loadPreview();
    }
  }

  async function loadPreview() {
    if (!currentDataset) return;
    const data = await API.get(`/api/datasets/${currentDataset}`);
    currentColumns = data.columns;
    $("#dataColumns").innerHTML = data.columns.map(c => `<span class="hash-pair" style="border-color:var(--border)"><span class="k">${c}</span></span>`).join("");
    renderTable($("#dataTable"), data.columns, data.rows, data.total);
  }

  $("#datasetSelect").onchange = () => { currentDataset = $("#datasetSelect").value; loadPreview().catch(e => toast(e.message, "error")); };

  $("#generateBtn").onclick = async () => {
    try {
      await API.post("/api/datasets/generate", {
        name: $("#datasetName").value || "demo",
        count: Number($("#datasetCount").value) || 100,
        seed: $("#datasetSeed").value ? Number($("#datasetSeed").value) : null,
      });
      toast("Dataset generado (reproducible por semilla)", "ok");
      await refresh();
    } catch (error) { toast(error.message, "error"); }
  };

  $("#uploadBtn").onclick = async () => {
    try {
      const file = $("#csvFile").files[0];
      let response;
      if (file) {
        const form = new FormData();
        form.append("file", file);
        form.append("name", $("#csvName").value || file.name);
        response = await fetch("/api/datasets/upload", { method: "POST", body: form });
        const body = await response.json();
        if (!body.success) throw new Error(body.error);
      } else {
        response = await API.post("/api/datasets/upload", { name: $("#csvName").value || "csv", content: $("#csvText").value });
      }
      toast("CSV cargado", "ok");
      await refresh();
    } catch (error) { toast(error.message, "error"); }
  };

  function selectedColumn() {
    const column = $("#opColumn").value.trim();
    if (!column) { toast("Indique la columna", "error"); return null; }
    return column;
  }

  $("#filterBtn").onclick = async () => {
    try {
      const column = selectedColumn(); if (!column) return;
      const data = await API.post(`/api/datasets/${currentDataset}/filter`, {
        column, operator: $("#opOperator").value, value: $("#opValue").value,
      });
      resultRows = data.rows;
      renderTable($("#resultTable"), currentColumns, data.rows, data.kept);
      $("#opResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">filas que pasan</div><div class="v">${data.kept}</div></div>
          <div class="info-chip"><div class="k">de un total de</div><div class="v">${data.total}</div></div>
          <div class="info-chip"><div class="k">comparaciones O(n)</div><div class="v">${fmt(data.comparisons)}</div></div>
        </div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#sortColBtn").onclick = async () => {
    try {
      const column = selectedColumn(); if (!column) return;
      const data = await API.post(`/api/datasets/${currentDataset}/sort`, {
        column, ascending: $("#opAsc").value === "1",
      });
      resultRows = data.rows;
      renderTable($("#resultTable"), currentColumns, data.rows);
      $("#opResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">comparaciones</div><div class="v">${fmt(data.comparisons)}</div></div>
          <div class="info-chip"><div class="k">intercambios (quick)</div><div class="v">${fmt(data.swaps)}</div></div>
          <div class="info-chip"><div class="k">algoritmo</div><div class="v neutral">Quick Sort propio O(n log n)</div></div>
        </div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  $("#transformBtn").onclick = async () => {
    try {
      const column = selectedColumn(); if (!column) return;
      const data = await API.post(`/api/datasets/${currentDataset}/transform`, {
        column, transform: $("#opTransform").value,
      });
      resultRows = data.rows;
      renderTable($("#resultTable"), currentColumns, data.rows);
      $("#opResult").innerHTML = `<div class="info-chip"><div class="k">celdas transformadas</div><div class="v">${data.transformed}</div></div>`;
      toast(`Transformación aplicada a ${data.transformed} celdas`, "ok");
    } catch (error) { toast(error.message, "error"); }
  };

  $("#dedupeBtn").onclick = async () => {
    try {
      const data = await API.post(`/api/datasets/${currentDataset}/dedupe`, {});
      $("#opResult").innerHTML = `
        <div class="info-grid">
          <div class="info-chip"><div class="k">duplicados eliminados</div><div class="v">${data.removed}</div></div>
          <div class="info-chip"><div class="k">filas restantes</div><div class="v">${data.remaining}</div></div>
        </div>`;
      toast("Duplicados eliminados", "ok");
      await loadPreview();
    } catch (error) { toast(error.message, "error"); }
  };

  $("#statsBtn").onclick = async () => {
    try {
      const data = await API.get(`/api/datasets/${currentDataset}/stats`);
      const entries = Object.entries(data.stats);
      $("#opResult").innerHTML = `<div class="info-grid">${entries.map(([col, s]) => `
        <div class="info-chip">
          <div class="k">${col} (${s.type})</div>
          <div class="v neutral" style="font-size:11px">${s.type === "numeric"
            ? `min ${fmt(s.min)} · max ${fmt(s.max)}<br>media ${fmt(s.mean)} · mediana ${fmt(s.median)}<br>σ ${fmt(s.std_dev)} · n ${fmt(s.count)}`
            : `${s.count} valores<br>${Object.entries(s.frequencies).slice(0, 3).map(([k, v]) => `${k}: ${v}`).join(", ")}`}</div>
        </div>`).join("")}</div>`;
    } catch (error) { toast(error.message, "error"); }
  };

  refresh().catch(e => toast(e.message, "error"));
};

/* ============================================================
   MÓDULO L — PROYECTOS Y ANÁLISIS
   ============================================================ */
Labs.projects = function () {
  let timeChart = null, opsChart = null, searchChart = null;

  $("#runSortBenchBtn").onclick = async () => {
    const btn = $("#runSortBenchBtn"); btn.disabled = true;
    try {
      const algorithms = ["bubble", "selection", "quick"].filter(a => $(`#bench_${a}`).checked);
      if (!algorithms.length) { toast("Seleccione al menos un algoritmo", "error"); return; }
      const sizes = [100, 1000, 10000, 100000].filter(s => $(`#size_${s}`).checked);
      if (!sizes.length) { toast("Seleccione al menos un tamaño", "error"); return; }
      toast("Ejecutando experimento… los tamaños grandes pueden tardar varios segundos", "");
      const data = await API.post("/api/benchmarks/sort", { algorithms, sizes });
      renderSortResults(data);
      toast("Experimento completado", "ok");
    } catch (error) { toast(error.message, "error"); }
    finally { btn.disabled = false; }
  };

  function renderSortResults(data) {
    const viable = data.results.filter(r => r.viable);
    const table = $("#benchTable");
    table.innerHTML = `<tr><th>Algoritmo</th><th>n</th><th>Tiempo (ms)</th><th>Comparaciones</th><th>Intercambios</th><th>Estado</th></tr>` +
      data.results.map(r => r.viable
        ? `<tr><td style="color:var(--text)">${r.algorithm}</td><td>${fmt(r.size)}</td><td>${fmt(r.time_ms)}</td><td>${fmt(r.comparisons)}</td><td>${fmt(r.swaps)}</td><td style="color:var(--ok)">ok</td></tr>`
        : `<tr><td style="color:var(--text)">${r.algorithm}</td><td>${fmt(r.size)}</td><td>—</td><td>—</td><td>—</td><td style="color:var(--warn)" title="${r.skipped_reason}">omitido</td></tr>`).join("");
    $("#benchNotes").innerHTML = data.notes.map(n => `<li>${n}</li>`).join("");

    if (timeChart) timeChart.destroy();
    timeChart = makeChart($("#benchTimeChart"), {
      type: "line",
      data: {
        labels: viable.map(r => r.size),
        datasets: [...new Set(viable.map(r => r.algorithm))].map((algorithm, i) => ({
          label: algorithm,
          data: viable.filter(r => r.algorithm === algorithm).map(r => r.time_ms),
          borderColor: CHART_COLORS[i], backgroundColor: CHART_COLORS[i] + "22",
          tension: .3, fill: false,
        })),
      },
      options: {
        scales: { y: { type: "logarithmic", title: { display: true, text: "ms (escala log)" } } },
        plugins: { title: { display: true, text: "Tiempo de ordenamiento vs tamaño de datos" } },
      },
    });
    if (opsChart) opsChart.destroy();
    opsChart = makeChart($("#benchOpsChart"), {
      type: "line",
      data: {
        labels: viable.map(r => r.size),
        datasets: [...new Set(viable.map(r => r.algorithm))].map((algorithm, i) => ({
          label: algorithm,
          data: viable.filter(r => r.algorithm === algorithm).map(r => r.comparisons),
          borderColor: CHART_COLORS[i], backgroundColor: CHART_COLORS[i] + "22",
          tension: .3, fill: false,
        })),
      },
      options: {
        scales: { y: { type: "logarithmic", title: { display: true, text: "comparaciones (escala log)" } } },
        plugins: { title: { display: true, text: "Operaciones elementales vs tamaño de datos" } },
      },
    });
  }

  $("#runSearchBenchBtn").onclick = async () => {
    const btn = $("#runSearchBenchBtn"); btn.disabled = true;
    try {
      const sizes = [100, 1000, 10000, 100000].filter(s => $(`#size_${s}`).checked);
      if (!sizes.length) { toast("Seleccione al menos un tamaño", "error"); return; }
      const data = await API.post("/api/benchmarks/search", { sizes });
      $("#searchBenchTable").innerHTML = `<tr><th>n</th><th>Linear (ms)</th><th>Compar. linear</th><th>Binary prep. orden (ms)</th><th>Binary búsqueda (ms)</th><th>Compar. binary</th></tr>` +
        data.results.map(r => `<tr>
          <td>${fmt(r.size)}</td>
          <td>${fmt(r.linear.time_ms, 4)}</td><td>${fmt(r.linear.comparisons)}</td>
          <td>${fmt(r.binary.prep_time_ms, 4)}</td><td>${fmt(r.binary.search_time_ms, 5)}</td><td>${fmt(r.binary.comparisons)}</td></tr>`).join("");
      if (searchChart) searchChart.destroy();
      searchChart = makeChart($("#searchBenchChart"), {
        type: "bar",
        data: {
          labels: data.results.map(r => r.size),
          datasets: [
            { label: "Linear: comparaciones", data: data.results.map(r => r.linear.comparisons), backgroundColor: CHART_COLORS[0] },
            { label: "Binary: comparaciones", data: data.results.map(r => r.binary.comparisons), backgroundColor: CHART_COLORS[1] },
          ],
        },
        options: {
          scales: { y: { type: "logarithmic" } },
          plugins: { title: { display: true, text: "Comparaciones por búsqueda (escala log)" } },
        },
      });
      toast("Benchmark de búsqueda completado", "ok");
    } catch (error) { toast(error.message, "error"); }
    finally { btn.disabled = false; }
  };
};

/* ============================================================
   Despachador
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  // Los slugs con guion ("stack-queue", "search-sort") se mapean a camelCase.
  const key = page ? page.replace(/-([a-z])/g, (_, c) => c.toUpperCase()) : null;
  if (key && Labs[key]) {
    try { Labs[key](); } catch (error) { toast(`Error al iniciar el laboratorio: ${error.message}`, "error"); }
  }
});
