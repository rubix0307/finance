function tabsHandler() {
    return {
        tab: 'main',
        validTabs: ['main', 'menu', 'account'],
        init() {
            const hash = window.location.hash.replace('#', '');
            if (this.validTabs.includes(hash)) {
                this.tab = hash;
            } else {
                this.tab = 'main';
            }
            history.replaceState(null, null, `#${this.tab}`);

            window.addEventListener('hashchange', () => {
                const newHash = window.location.hash.replace('#', '');
                if (this.validTabs.includes(newHash)) {
                    this.tab = newHash;
                }
            });
        },

        setTab(newTab) {
            if (this.validTabs.includes(newTab)) {
                this.tab = newTab;
                history.replaceState(null, null, `#${newTab}`);
            }
        }
    }
}