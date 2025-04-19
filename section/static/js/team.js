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

function base64urlEncode(obj) {
    const b64 = btoa(JSON.stringify(obj));
    return b64
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

document.addEventListener('alpine:init', () => {
    Alpine.data('teamComponent', () => ({
        meId: null,
        ownerId: null,
        confirmationId: null,

        init() {
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.ready();
            }
            this.updateIds();
            this.$watch(
                () => Alpine.store('appData').me.id,
                () => this.updateIds()
            );
            this.$watch(
                () => Alpine.store('appData').current_section,
                () => this.updateIds()
            );
        },

        updateIds() {
            const store = Alpine.store('appData');
            this.meId = store.me?.id ?? null;
            const section = store.current_section;
            this.ownerId = section?.users?.find(u => u.is_owner)?.id ?? null;
        },

        async handleDelete(personId) {
            if (this.confirmationId !== personId) {
                this.confirmationId = personId;
                return;
            }
            try {
                const store = Alpine.store('appData');
                const sectionId = store.current_section.id;

                await window.deleteMembership(sectionId, personId);
                this.confirmationId = null;
            } catch (err) {
                console.error('Ошибка удаления пользователя:', err);
                this.confirmationId = null;
            }
        }
    }));
});

async function deleteMembership(sectionId, personId) {
  const url = `/api/sections/${sectionId}/memberships/${personId}/delete`;
  const csrfToken = getCookie('csrftoken');

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
  });

  if (!response.ok) {
    throw new Error('Не удалось удалить пользователя на сервере');
  }

  const store = Alpine.store('appData');
  const meId    = store.me?.id ?? null;
  const section = store.current_section;
  const ownerId = section?.users?.find(u => u.is_owner)?.id ?? null;

  store.current_section.users = section.users
    .filter(u => u.id !== personId);

  store.sections = store.sections.map(s => {
    if (s.id === sectionId) {
      return {
        ...s,
        users: s.users.filter(u => u.id !== personId)
      };
    }
    return s;
  });

  if (personId === meId && meId !== ownerId) {
    store.nextSection();
    store.sections = store.sections.filter(s => s.id !== sectionId);
  }
}