function tabsHandler() {
    return {
        get tab() {
          return Alpine.store('tabs').tab;
        },
        set tab(value) {
          Alpine.store('tabs').tab = value;
        },

        validTabs: ['main', 'menu', 'account'],

        currentIcons: {
          menu: 'toast',
          account: 'account',
        },
        previousIcons: {
          menu: null,
          account: null,
        },
        animate: {
          menu: false,
          account: false,
        },

        init_tabs() {
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

        setTab(target) {
          let newTab = target === this.tab ? 'main' : target;
          this.tab = newTab;
          history.replaceState(null, null, `#${newTab}`);

          let newMenuIcon = newTab === 'menu' ? 'home' : 'toast';
          let newAccountIcon = newTab === 'account' ? 'home' : 'account';

          if (this.currentIcons.menu !== newMenuIcon) {
            this.animate.menu = false;
            requestAnimationFrame(() => this.animate.menu = true);
            this.previousIcons.menu = this.currentIcons.menu;
            this.currentIcons.menu = newMenuIcon;
          }

          if (this.currentIcons.account !== newAccountIcon) {
            this.animate.account = false;
            requestAnimationFrame(() => this.animate.account = true);
            this.previousIcons.account = this.currentIcons.account;
            this.currentIcons.account = newAccountIcon;
          }
        }
      }
}