const difficultyConfig = {
  easy: { minDelay: 1500, maxDelay: 4500, label: "Easy" },
  normal: { minDelay: 1000, maxDelay: 4000, label: "Normal" },
  hard: { minDelay: 700, maxDelay: 3000, label: "Hard" }
};

const gameAreaInner = document.getElementById("game-area-inner");
const startBtn = document.getElementById("start-btn");
const resetBtn = document.getElementById("reset-highscores");
const difficultySelect = document.getElementById("difficulty");
const modeLabel = document.getElementById("mode-label");

const state = new GameState(gameAreaInner);
const timer = new Timer();
const ui = new GameUI();
const stats = new Stats();

let currentDifficulty = "normal";
modeLabel.textContent = difficultyConfig[currentDifficulty].label;
stats.setDifficulty(currentDifficulty);

function randomDelay() {
  const cfg = difficultyConfig[currentDifficulty];
  return cfg.minDelay + Math.random() * (cfg.maxDelay - cfg.minDelay);
}

function startRound() {
  timer.clear();
  state.set(STATES.WAITING);
  ui.waiting();

  const delay = randomDelay();
  const startTime = Date.now();

  timer.schedule(delay, () => {
    state.set(STATES.READY);
    ui.ready();
  });

  const tick = () => {
    if (!state.is(STATES.WAITING)) return;
    const left = Math.max(0, delay - (Date.now() - startTime));
    ui.countdown.textContent =
      left > 0 ? `~${(left / 1000).toFixed(1)}s` : "Any moment…";
    requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);
}

function react() {
  if (state.is(STATES.WAITING)) {
    timer.clear();
    state.set(STATES.TOO_SOON);
    ui.tooSoon();
    stats.resetOnTooSoon();
    return;
  }

  if (state.is(STATES.READY)) {
    const ms = timer.reactionTime();
    state.set(STATES.RESULT);
    ui.result(ms);
    stats.updateWithReaction(ms);
    return;
  }

  startRound();
}

startBtn.addEventListener("click", startRound);
document.getElementById("game-area").addEventListener("click", react);
window.addEventListener("keydown", e => {
  if (e.code === "Space") {
    e.preventDefault();
    react();
  }
});

difficultySelect.addEventListener("change", () => {
  currentDifficulty = difficultySelect.value;
  modeLabel.textContent = difficultyConfig[currentDifficulty].label;
  stats.setDifficulty(currentDifficulty);
  state.set(STATES.IDLE);
  ui.idle();
});

resetBtn.addEventListener("click", () => {
  if (confirm("Reset all stored highscores?")) {
    stats.resetAlltime();
  }
});

ui.idle();
