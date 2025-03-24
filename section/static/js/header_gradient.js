function interpolateColor(color1, color2, factor) {
  const c1 = color1.match(/\w\w/g).map(x => parseInt(x, 16));
  const c2 = color2.match(/\w\w/g).map(x => parseInt(x, 16));
  const result = c1.map((c, i) => Math.round(c + (c2[i] - c) * factor));
  return '#' + result.map(c => c.toString(16).padStart(2, '0')).join('');
}

function generateGradientSteps(start, end, steps) {
  const gradient = [];
  for (let i = 0; i < steps; i++) {
    gradient.push(interpolateColor(start, end, i / (steps - 1)));
  }
  return gradient;
}

const colors = generateGradientSteps('C2B5FF', 'F0F0F0', 50);
const metaTag = document.querySelector('meta[name="theme-color"]');
const header = document.querySelector('header');

window.addEventListener('scroll', () => {
  const maxScroll = 50;
  const scrollY = Math.min(window.scrollY, maxScroll);
  const index = Math.floor((scrollY / maxScroll) * (colors.length - 1));
  const color = '#' + colors[index].replace('#', '');

  metaTag.setAttribute('content', color);
  header.style.backgroundColor = color;
});