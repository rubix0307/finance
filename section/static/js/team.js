function getSortedSectionUsers() {
    const section = Alpine.store('appData').current_section;
    const ownerId = section?.users.find(u => u.is_owner)?.id;

    if (!section || !Array.isArray(section.users)) return [];

    return [...section.users].sort((a, b) => {
        if (a.id === ownerId) return -1;
        if (b.id === ownerId) return 1;
        return a.id - b.id;
    });
}