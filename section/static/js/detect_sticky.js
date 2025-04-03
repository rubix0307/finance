document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('#feed .header');
  if (!header) return;

  const sentinel = document.createElement('div');
  sentinel.style.position = 'absolute';
  sentinel.style.top = '-5px';
  sentinel.style.width = '1px';
  sentinel.style.height = '1px';
  sentinel.style.pointerEvents = 'none';
  sentinel.style.opacity = '0';
  header.parentNode.insertBefore(sentinel, header);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.intersectionRatio < 1) {
        header.classList.add('sticky');
      } else {
        header.classList.remove('sticky');
      }
    });
  }, {
    threshold: [1]
  });

  observer.observe(sentinel);
});