document.addEventListener('alpine:init', () => {
  Alpine.store('chart_nav', {
  ranges: ['week', 'month', 'year'],
  groupsOptions: {
    week: ['daily'],
    month: ['daily', 'weekly'],
    year: ['weekly', 'monthly']
  },

  selectedRange: 'week',
  selectedGroup: 'daily',

  orderMapping: {
    daily: 1,
    weekly: 2,
    monthly: 3
  },

  get availableGroups() {
    return this.groupsOptions[this.selectedRange];
  },

  setRange(newRange) {
    this.selectedRange = newRange;
    if (!this.availableGroups.includes(this.selectedGroup)) {
      const currentOrder = this.orderMapping[this.selectedGroup] || 0;
      const minAvailableOrder = this.orderMapping[this.availableGroups[0]];
      const maxAvailableOrder = this.orderMapping[this.availableGroups[this.availableGroups.length - 1]];

      if (currentOrder < minAvailableOrder) {
        this.selectedGroup = this.availableGroups[0];
      }
      else if (currentOrder > maxAvailableOrder) {
        this.selectedGroup = this.availableGroups[this.availableGroups.length - 1];
      }
      else {
        this.selectedGroup = this.availableGroups[0];
      }
    }
  },

  setGroup(newGroup) {
    if (this.availableGroups.includes(newGroup)) {
      this.selectedGroup = newGroup;
    }
  }
});
});