const timer = document.querySelector('[data-remaining]');
if (timer) {
  const deadline = Date.now() + Number(timer.dataset.remaining) * 1000;
  const tick = () => {
    const seconds = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    document.getElementById('clock').textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    if (seconds === 0) { document.getElementById('answers').requestSubmit(); }
    else { setTimeout(tick, 500); }
  };
  tick();
}

const conversation = document.querySelector("[data-chat]");
if (conversation) conversation.scrollTop = conversation.scrollHeight;
