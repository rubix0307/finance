document.addEventListener('alpine:init', () => {
    Alpine.store('plans', {
        plans: [],
        current: 0,

        prev() {
            if (!this.plans.length) return;
            this.current = (this.current - 1 + this.plans.length) % this.plans.length;
        },

        next() {
            if (!this.plans.length) return;
            this.current = (this.current + 1) % this.plans.length;
        },

        get currentPlan() {
            return this.plans[this.current];
        }
    });

    const app = Alpine.store('appData');
    if (app.plans && app.plans.length) {
        Alpine.store('plans').plans = app.plans;
        Alpine.store('plans').current = 0;
    }
    app.$subscribe('appData', (newPlans) => {
        if (Array.isArray(newPlans) && newPlans.length) {
            Alpine.store('plans').plans = newPlans;
            Alpine.store('plans').current = 0;
        }
    });
});