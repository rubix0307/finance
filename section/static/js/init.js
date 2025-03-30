
document.addEventListener('alpine:init', () => {
    Alpine.store('appData', {
        sections: [],
        currencies: [],
        current_section: null,
        me: {},
        loading: true,

        init() {
            Alpine.effect(() => {
                const currencies = Alpine.store('appData').currencies;
                if (currencies && currencies.length) {
                    // Следим за изменением current_section
                    Alpine.watch(
                        () => Alpine.store('appData').current_section,
                        () => {
                            queueMicrotask(() => {
                                // Это тоже не будет работать здесь — потому что this.$refs нет в store!
                                // this.$refs.currencyList?.scrollTo(...) — ❌
                                // Лучше перенести это в x-effect в компоненте (в шаблоне)
                                // или выбрать через document.querySelector
                                document.querySelector('[x-ref="currencyList"]')?.scrollTo({ top: 0, behavior: 'auto' });
                            });
                        }
                    );
                }
            });
        },

        async init_app() {
            try {
                const [currenciesResponse, sectionsResponse, userResponse] = await Promise.all([
                    fetch('/api/currencies/'),
                    fetch('/api/sections/'),
                    fetch('/api/users/me/'),
                ]);

                if (currenciesResponse.ok) {
                    this.currencies = await currenciesResponse.json();
                }

                if (sectionsResponse.ok) {
                    this.sections = await sectionsResponse.json();
                    this.current_section = this.sections.find(s => s.is_base) || null;
                }

                if (userResponse.ok) {
                    this.me = await userResponse.json();
                }
            } catch (err) {
                console.error('Ошибка при загрузке данных:', err);
            } finally {
                this.loading = false;
            }
        },
        nextSection() {
            if (this.sections.length <= 1) return;

            const currentIndex = this.sections.findIndex(s => s.id === this.current_section?.id);
            const nextIndex = (currentIndex + 1) % this.sections.length;
            this.current_section = this.sections[nextIndex];
        },

        prevSection() {
            if (this.sections.length <= 1) return;

            const currentIndex = this.sections.findIndex(s => s.id === this.current_section?.id);
            const prevIndex = (currentIndex - 1 + this.sections.length) % this.sections.length;
            this.current_section = this.sections[prevIndex];
        }
    });

    // Инициализация
    Alpine.store('appData').init_app();
});
