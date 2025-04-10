class TelegramAppHelper {
    constructor() {
        window.addEventListener('DOMContentLoaded', () => {
            this.webApp = window.Telegram?.WebApp;

            if (!this.webApp) {
                console.warn("Telegram WebApp не найден.");
                return;
            }

            this.webApp.expand();
        });
    }

    setHeaderColorFromVar(varName) {
        if (!this.webApp) return;

        const root = document.documentElement;
        const color = getComputedStyle(root).getPropertyValue(varName).trim();

        if (color) {
            this.webApp.setHeaderColor(color);
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const tgHelper = new TelegramAppHelper();
    tgHelper.setHeaderColorFromVar('--main_purple');
})