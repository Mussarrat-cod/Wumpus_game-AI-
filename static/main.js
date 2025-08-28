const gridEl = document.getElementById("grid");
const statusEl = document.getElementById("statusText");
const scoreEl = document.getElementById("score");
const arrowEl = document.getElementById("arrow");
const wumpusEl = document.getElementById("wumpus");

const breezeEl = document.getElementById("breeze");
const stenchEl = document.getElementById("stench");
const glitterEl = document.getElementById("glitter");
const screamEl = document.getElementById("scream");

const sizeInput = document.getElementById("size");
const pitsInput = document.getElementById("pits");
const newBtn = document.getElementById("newGame");
const aiToggle = document.getElementById("aiToggle");
const aiStep = document.getElementById("aiStep");
const revealBtn = document.getElementById("reveal");

const grabBtn = document.getElementById("grabBtn");
const climbBtn = document.getElementById("climbBtn");
const shootDir = document.getElementById("shootDir");

let currentState = null;

async function post(url, data = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}
async function get(url) {
  const res = await fetch(url);
  return res.json();
}

function emojiFor(cell) {
  if (cell.agent) return "🤖";
  if (cell.gold) return "💰";
  if (cell.wumpus) return "👹";
  if (cell.pit) return "🕳️";
  return "";
}

function render(state) {
  currentState = state;
  const N = state.size;
  gridEl.style.gridTemplateColumns = `repeat(${N}, 64px)`;
  gridEl.innerHTML = "";

  for (let i = 0; i < N; i++) {
    for (let j = 0; j < N; j++) {
      const cell = state.tiles[i][j];
      const div = document.createElement("div");
      div.className = "cell";
      if (cell.safe) div.classList.add("safe");
      if (cell.visited) div.classList.add("visited");
      if (cell.agent) div.classList.add("agent");
      if (!cell.discovered && !cell.agent) {
        div.textContent = "❔";
      } else {
        div.textContent = emojiFor(cell);
      }
      // tiny hint coords
      const hint = document.createElement("span");
      hint.className = "hint";
      hint.textContent = `${i},${j}`;
      div.appendChild(hint);
      gridEl.appendChild(div);
    }
  }

  statusEl.textContent = state.status;
  scoreEl.textContent = state.score;
  arrowEl.textContent = state.arrow_available ? "Yes" : "No";
  wumpusEl.textContent = state.wumpus_alive ? "Yes" : "No";

  breezeEl.textContent = state.percepts.breeze ? "Yes" : "No";
  stenchEl.textContent = state.percepts.stench ? "Yes" : "No";
  glitterEl.textContent = state.percepts.glitter ? "Yes" : "No";
  screamEl.textContent = state.percepts.scream ? "Yes" : "No";
}

async function refresh() {
  const st = await get("/api/state");
  render(st);
}

async function init() {
  await post("/api/new", { size: parseInt(sizeInput.value, 10), pits: parseInt(pitsInput.value, 10) });
  await refresh();
}

newBtn.addEventListener("click", async () => {
  await post("/api/new", { size: parseInt(sizeInput.value, 10), pits: parseInt(pitsInput.value, 10) });
  await refresh();
});

document.querySelectorAll("[data-move]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const dir = btn.getAttribute("data-move");
    const st = await post("/api/move", { direction: dir });
    render(st);
  });
});

grabBtn.addEventListener("click", async () => {
  render(await post("/api/grab", {}));
});

climbBtn.addEventListener("click", async () => {
  render(await post("/api/climb", {}));
});

shootDir.addEventListener("change", () => {});
shootDir.addEventListener("dblclick", async () => {
  render(await post("/api/shoot", { direction: shootDir.value }));
});

aiToggle.addEventListener("change", async () => {
  await post("/api/ai/toggle", { enabled: aiToggle.checked });
  await refresh();
});

aiStep.addEventListener("click", async () => {
  const st = await post("/api/ai/step", {});
  render(st);
});

// Keyboard shortcuts
document.addEventListener("keydown", async (e) => {
  const map = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right" };
  if (map[e.key]) {
    e.preventDefault();
    render(await post("/api/move", { direction: map[e.key] }));
  } else if (e.key.toLowerCase() === "g") {
    e.preventDefault();
    render(await post("/api/grab", {}));
  } else if (e.key.toLowerCase() === "c") {
    e.preventDefault();
    render(await post("/api/climb", {}));
  } else if (e.key.toLowerCase() === "s") {
    e.preventDefault();
    render(await post("/api/shoot", { direction: shootDir.value }));
  }
});

revealBtn.addEventListener("click", async () => {
  render(await post("/api/reveal", {}));
});

init();
