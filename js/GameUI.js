class GameUI {
  constructor() {
    this.prompt = document.getElementById("prompt");
    this.message = document.getElementById("message");
    this.countdown = document.getElementById("countdown");
  }

  idle() {
    this.prompt.textContent = "Ready?";
    this.message.innerHTML =
      'Click <span class="highlight">Start round</span>, then wait for green.';
    this.countdown.textContent = "";
  }

  waiting() {
    this.prompt.textContent = "Wait for green…";
    this.message.innerHTML =
      'Do <span class="highlight">not</span> click yet.';
    this.countdown.textContent = "Get ready…";
  }

  ready() {
    this.prompt.textContent = "NOW!";
    this.message.innerHTML =
      'Tap <span class="highlight">now</span>!';
    this.countdown.textContent = "";
  }

  tooSoon() {
    this.prompt.textContent = "Too early!";
    this.message.textContent = "You clicked before green.";
    this.countdown.textContent = "Click or press space to reset.";
  }

  result(ms) {
    this.prompt.textContent = "Result";
    this.message.innerHTML =
      `Your time: <span class="highlight">${ms} ms</span>`;
    this.countdown.textContent =
      "Click or press space to start a new round.";
  }
}
