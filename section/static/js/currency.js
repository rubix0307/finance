document.addEventListener('alpine:init', () => {
    Alpine.store('currency', {
        open: false,
        query: '',
        isReady: false,

        init() {
            Alpine.watch(() => Alpine.store('appData').currencies, (currencies) => {
                if (currencies && currencies.length) {
                    this.isReady = true;
                    Alpine.watch(() => Alpine.store('appData').current_section, () => {
                        queueMicrotask(() => {
                            document.querySelector('[x-ref="currencyList"]')?.scrollTo({ top: 0, behavior: 'auto' });
                        });
                    });
                }
            });
        },

        currencyToggle() {
            if (!this.isReady) return;

            this.open = !this.open;
            if (!this.open) this.query = '';
            document.querySelector('[x-ref="currencyList"]')?.scrollTo({ top: 0, behavior: 'auto' });
        }
    });

    Object.defineProperty(Alpine.store('currency'), 'getCurrentCurrency', {
        get() {
            const currentSection = Alpine.store('appData').current_section;
            const me = Alpine.store('appData').me;
            const sectionMe = currentSection?.users.find(user => user.id === me.id);
            return sectionMe?.currency || null;
        }
    });

    Object.defineProperty(Alpine.store('currency'), 'getFilteredCurrencies', {
        get() {
            if (!Alpine.store('currency').isReady) return [];

            const all = Alpine.store('appData').currencies || [];
            const query = Alpine.store('currency').query.toLowerCase();
            const current = Alpine.store('currency').getCurrentCurrency;

            let filtered = all.filter(c =>
                c.code.toLowerCase().includes(query) &&
                (!current || c.code !== current.code)
            );

            if (current && current.code.toLowerCase().includes(query)) {
                return [current, ...filtered];
            }

            return filtered;
        }
    });
});