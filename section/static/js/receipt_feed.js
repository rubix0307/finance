document.addEventListener('alpine:init', () => {
    Alpine.store('receipts_feed', {
        sections: {},
        activeSection: null,
        defaultSize: 10,
        initialized: false,
        showPhotos: true,

        initForCurrentSection() {
            const appData = Alpine.store('appData');
            this.setActiveSection(appData.current_section);
        },

        initSection(sectionId) {
            if (!this.sections[sectionId]) {
                this.sections[sectionId] = {
                    receipts: [],
                    total: 0,
                    currentPage: 1,
                    size: this.defaultSize,
                    pagesCount: 0,
                    loading: false,
                    error: null,
                    fetched: false
                };
            }
        },

        setActiveSection(sectionObj) {
            const sectionId = sectionObj.id;
            this.activeSection = sectionId;
            this.initSection(sectionId);
            const sectionData = this.sections[sectionId];
            if (!sectionData.fetched && sectionData.receipts.length === 0 && !sectionData.loading) {
                this.loadPage(1);
            }
        },

        loadPage(page = 1) {
            const sectionData = this.sections[this.activeSection];
            sectionData.loading = true;
            sectionData.error = null;
            const url = `/api/sections/${this.activeSection}/receipts/?page=${page}&size=${sectionData.size}`;
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error('Ошибка при получении чеков');
                    return response.json();
                })
                .then(data => {
                    sectionData.total = data.total;
                    sectionData.pagesCount = Math.ceil(data.total / sectionData.size);
                    if (data.total === 0) {
                        sectionData.fetched = true;
                    }
                    const apiSize = data.size;
                    if (apiSize && apiSize != sectionData.size) {
                        this.defaultSize = apiSize;
                        sectionData.size = apiSize;
                    }
                    const newPage = {
                        page: page,
                        size: sectionData.size,
                        data: data.results
                    };
                    sectionData.receipts = sectionData.receipts.filter(item => item.page !== page);
                    sectionData.receipts.push(newPage);
                    sectionData.receipts.sort((a, b) => a.page - b.page);
                })
                .catch(err => {
                    sectionData.error = err.message;
                    console.error(err);
                })
                .finally(() => {
                    sectionData.loading = false;
                });
        },

        getCurrentPageItems() {
            const sectionData = this.sections[this.activeSection];
            const pageObj = sectionData.receipts.find(item => item.page === sectionData.currentPage);
            if ((!pageObj || pageObj.data.length === 0) && !sectionData.loading && !sectionData.fetched) {
                this.loadPage(sectionData.currentPage);
                return [];
            }
            return pageObj ? pageObj.data : [];
        },

        setPageSize(newSize) {
            const sectionData = this.sections[this.activeSection];
            sectionData.receipts = [];
            sectionData.size = newSize;
            sectionData.currentPage = 1;
            sectionData.pagesCount = 0;
            sectionData.total = 0;
            sectionData.fetched = false;
            this.loadPage(1);
        },

        refresh() {
            const sectionData = this.sections[this.activeSection];
            sectionData.receipts = sectionData.receipts.filter(item => item.page !== sectionData.currentPage);
            sectionData.fetched = false;
            this.loadPage(sectionData.currentPage);
        }
    });

    // Эффект будет отслеживать изменения appData.current_section и вызывать setActiveSection
    Alpine.effect(() => {
        const appData = Alpine.store('appData');
        if (appData.me && appData.me.id && appData.current_section && appData.current_section.id) {
            Alpine.store('receipts_feed').setActiveSection(appData.current_section);
        }
    });
});
