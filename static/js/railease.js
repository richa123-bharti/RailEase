document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.train-card').forEach((card, index) => {
    card.style.animationDelay = `${index * 70}ms`;
    card.classList.add('reveal-card');
  });
});
