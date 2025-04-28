document.addEventListener('alpine:init', () => {
    Alpine.store('plans', {
        plans: [],
        current: 0,
        initialDefaultSet: false,

        prev() {
            if (!this.plans.length) return;
            this.current = (this.current - 1 + this.plans.length) % this.plans.length;
        },

        next() {
            if (!this.plans.length) return;
            this.current = (this.current + 1) % this.plans.length;
        },

        setCurrentBySlug(slug) {
            const idx = this.plans.findIndex(p => p.slug === slug);
            this.current = idx >= 0 ? idx : 0;
        },

        get currentPlan() {
            return this.plans[this.current] || {};
        },

        get currentSubscription() {
            const subs = Array.isArray(Alpine.store('appData').me.active_subs)
                ? Alpine.store('appData').me.active_subs
                : [];
            return subs.find(s => s.plan.slug === this.currentPlan.slug) || null;
        }
    });


    function priceSort(a, b) {
        if (a.price_stars == null && b.price_stars == null) return 0;
        if (a.price_stars == null) return -1;
        if (b.price_stars == null) return 1;
        return a.price_stars - b.price_stars;
    }

    Alpine.effect(() => {
        const serverPlans = Alpine.store('appData').plans;
        const userSubs = Array.isArray(Alpine.store('appData').me.active_subs)
            ? Alpine.store('appData').me.active_subs
            : [];

        if (!Array.isArray(serverPlans)) return;

        const prevSlug = Alpine.store('plans').currentPlan.slug;

        const union = {};
        serverPlans.forEach(p => union[p.slug] = p);
        userSubs.forEach(s => union[s.plan.slug] = s.plan);

        const sorted = Object.values(union).sort(priceSort);
        Alpine.store('plans').plans = sorted;

        if (!Alpine.store('plans').initialDefaultSet && userSubs.length) {
            const richest = userSubs.reduce((best, cur) =>
                ((best.plan.price_stars ?? -1) >= (cur.plan.price_stars ?? -1))
                    ? best
                    : cur
            );
            Alpine.store('plans').setCurrentBySlug(richest.plan.slug);
            Alpine.store('plans').initialDefaultSet = true;

        } else {
            Alpine.store('plans').setCurrentBySlug(prevSlug);
        }
    });
});