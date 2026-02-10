class Timer {
  constructor() {
    this.timeoutId = null;
    this.startTime = 0;
  }

  clear() {
    clearTimeout(this.timeoutId);
    this.timeoutId = null;
  }

  schedule(delay, callback) {
    this.clear();
    this.timeoutId = setTimeout(() => {
      this.startTime = Date.now();
      callback();
    }, delay);
  }

  reactionTime() {
    return Date.now() - this.startTime;
  }
}
