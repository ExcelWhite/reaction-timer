class Stats {
  constructor() {
    this.lastTimeEl = document.getElementById("last-time");
    this.lastCommentEl = document.getElementById("last-comment");
    this.sessionBestEl = document.getElementById("session-best");
    this.alltimeBestEl = document.getElementById("alltime-best");
    this.streakCountEl = document.getElementById("streak-count");
    this.fastStreakEl = document.getElementById("fast-streak");

    this.sessionBest = null;
    this.streak = 0;
    this.fastStreak = 0;
    this.currentDifficulty = "normal";
  }

  setDifficulty(diff) {
    this.currentDifficulty = diff;
    this.sessionBest = null;
    this.sessionBestEl.textContent = "–";
    this.streak = 0;
    this.fastStreak = 0;
    this.updateStreakUI();
    this.loadAlltimeBest();
  }

  classify(ms) {
    if (ms < 150) return "insane";
    if (ms < 220) return "great";
    if (ms < 300) return "good";
    if (ms < 380) return "ok";
    if (ms < 500) return "slow";
    return "very-slow";
  }

  comment(ms) {
    return {
      insane: "Lightning fast! 🚀",
      great: "Amazing reaction.",
      good: "Solid reflexes.",
      ok: "Not bad — you can go faster.",
      slow: "A bit slow. Stay focused.",
      "very-slow": "Everyone has off rounds."
    }[this.classify(ms)];
  }

  updateWithReaction(ms) {
    this.lastTimeEl.textContent = ms;
    this.lastCommentEl.textContent = this.comment(ms);

    if (this.sessionBest === null || ms < this.sessionBest) {
      this.sessionBest = ms;
      this.sessionBestEl.textContent = ms;
    }

    const key = `reaction-best-${this.currentDifficulty}`;
    const stored = localStorage.getItem(key);
    let alltime = stored ? Number(stored) : null;

    if (!alltime || ms < alltime) {
      alltime = ms;
      localStorage.setItem(key, ms);
    }

    this.alltimeBestEl.textContent = alltime ?? "–";

    this.streak++;
    this.fastStreak = ms < 250 ? this.fastStreak + 1 : 0;
    this.updateStreakUI();
  }

  updateStreakUI() {
    this.streakCountEl.textContent = this.streak;
    this.fastStreakEl.textContent = this.fastStreak;
  }

  loadAlltimeBest() {
    const key = `reaction-best-${this.currentDifficulty}`;
    const stored = localStorage.getItem(key);
    this.alltimeBestEl.textContent = stored ? Number(stored) : "–";
  }

  resetAlltime() {
    ["easy", "normal", "hard"].forEach(d =>
      localStorage.removeItem(`reaction-best-${d}`)
    );
    this.loadAlltimeBest();
  }

  resetOnTooSoon() {
    this.streak = 0;
    this.fastStreak = 0;
    this.updateStreakUI();
  }
}
