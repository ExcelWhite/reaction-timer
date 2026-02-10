const STATES = {
  IDLE: "idle",
  WAITING: "waiting",
  READY: "ready",
  TOO_SOON: "too-soon",
  RESULT: "result"
};

class GameState {
  constructor(gameAreaInner) {
    this.gameAreaInner = gameAreaInner;
    this.current = STATES.IDLE;
  }

  set(nextState) {
    this.gameAreaInner.classList.remove(
      STATES.IDLE,
      STATES.WAITING,
      STATES.READY,
      STATES.TOO_SOON,
      STATES.RESULT
    );
    this.gameAreaInner.classList.add(nextState);
    this.current = nextState;
  }

  is(state) {
    return this.current === state;
  }
}
