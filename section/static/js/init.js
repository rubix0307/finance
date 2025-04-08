document.addEventListener('alpine:init', () => {
    Alpine.store('appData', {
        sections: [],
        currencies: [],
        current_section: null,
        me: {},
        loading: true,

        init() {
            Alpine.effect(() => {
                const currencies = this.currencies;
                if (currencies && currencies.length) {
                    // Следим за изменением current_section и выполняем скроллинг списка валют
                    Alpine.watch(
                        () => this.current_section,
                        () => {
                            queueMicrotask(() => {
                                document.querySelector('[x-ref="currencyList"]')?.scrollTo({top: 0, behavior: 'auto'});
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
        },

        // Новый метод: отправка запроса на API для обновления названия текущей секции
        async apiUpdateCurrentSectionName(newName) {
            const currentSection = this.current_section;
            if (!currentSection) return;

            const url = `/api/sections/${currentSection.id}/`;
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({name: newName}),
                });

                if (!response.ok) {
                    throw new Error('Не удалось обновить секцию на сервере');
                }

                const updatedSectionData = await response.json();
                return updatedSectionData;
            } catch (err) {
                console.error("Ошибка запроса обновления секции:", err);
                throw err;
            }
        },

        // Новый метод: обновление данных секции в хранилище (и списка секций, и current_section)
        updateSectionDataInStore(updatedSectionData) {
            const index = this.sections.findIndex(s => s.id === updatedSectionData.id);
            if (index !== -1) {
                Object.assign(this.sections[index], updatedSectionData);
                Object.assign(this.current_section, updatedSectionData);
            }
        },

        // Новый метод: объединённый метод сохранения нового названия текущей секции.
        // Он отправляет запрос и при успешном ответе обновляет данные в Alpine.store.
        async saveCurrentSectionName(newName) {
            try {
                const updatedData = await this.apiUpdateCurrentSectionName(newName);
                this.updateSectionDataInStore(updatedData);
            } catch (error) {
                console.error("Ошибка сохранения нового имени секции:", error);
            }
        }
    });

    // Инициализация приложения
    Alpine.store('appData').init_app();
});