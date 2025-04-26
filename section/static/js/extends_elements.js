class VisibilityToggle extends HTMLElement {
    connectedCallback() {
        const el = this.querySelector('.to-show');
        if (!el) {
            return;
        }

        if (!el.style.display || el.style.display !== 'none') {
            el.style.display = 'none';
        }
        if (!el.hasAttribute('x-data')) {
            el.setAttribute('x-data', '{ open: false }');
        }
        if (!el.hasAttribute('x-on:visibility-changed')) {
            el.setAttribute('x-on:visibility-changed', 'open = $event.detail.visible');
        }
        if (!el.hasAttribute('x-show')) {
            el.setAttribute('x-show', 'open');
        }
        if (!el.hasAttribute('x-collapse')) {
            el.setAttribute('x-collapse', '');
        }

        const dir = this.getAttribute('direction') || 'bottom-up';
        const prefix = dir === 'top-down' ? 'fade-down' : 'fade-up';
        el.setAttribute('x-transition:enter', `${prefix}-enter-active`);
        el.setAttribute('x-transition:enter-start', `${prefix}-enter`);
        el.setAttribute('x-transition:enter-end', `${prefix}-enter-to`);
        el.setAttribute('x-transition:leave', `${prefix}-leave-active`);
        el.setAttribute('x-transition:leave-start', `${prefix}-leave`);
        el.setAttribute('x-transition:leave-end', `${prefix}-leave-to`);

        if (window.Alpine) {
            Alpine.initTree(el);
        }
        const threshold = parseFloat(this.getAttribute('threshold')) || 1.0;
        const obs = new IntersectionObserver(([entry]) => {
            const vis = entry.intersectionRatio >= threshold;
            el.dispatchEvent(new CustomEvent('visibility-changed', {
                detail: {visible: vis},
                bubbles: true
            }));
        }, {
            root: this.parentElement,
            threshold: [threshold]
        });
        obs.observe(this);
    }
}
customElements.define('visibility-toggle', VisibilityToggle);