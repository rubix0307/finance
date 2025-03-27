
document.addEventListener('alpine:init', () => {
    Alpine.store('appData', {
        sections: [],
        currencies: [],
        current_section: null,
        me: {},
        loading: true,

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
