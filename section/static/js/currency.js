function currencyHandler() {
    return {
        open: false,
        query: '',

        init() {
            this.$watch(() => Alpine.store('appData').current_section, () => {
                queueMicrotask(() => {
                    this.$refs.currencyList?.scrollTo({ top: 0, behavior: 'auto' });
                });
            });
        },

        currencyToggle() {
            if (!this.getCurrentCurrency?.code) {
                return;
            }

            this.open = !this.open;
            if (!this.open) this.query = '';
            this.$refs.currencyList?.scrollTo({ top: 0, behavior: 'auto' });
        },

        get getFilteredCurrencies() {
            const all = Alpine.store('appData').currencies || [];
            const query = this.query.toLowerCase();
            const current = this.getCurrentCurrency;

            let filtered = all.filter(c =>
                c.code.toLowerCase().includes(query) &&
                (!current || c.id !== current.id)
            );

            if (current && current.code.toLowerCase().includes(query)) {
                return [current, ...filtered];
            }

            return filtered;
        },

        get getCurrentCurrency() {
            let currentSection = Alpine.store('appData').current_section;
            let me = Alpine.store('appData').me;
            let section_me = currentSection?.users.find(user => user.id === me.id);

            return section_me?.currency || null;
        }
    }
}