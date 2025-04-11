class TelegramAppHelper {
  constructor(webApp) {
    this.webApp = webApp;
    this.webApp.expand();
  }

  setHeaderColorFromVar(varName) {
    const root = document.documentElement;
    const color = getComputedStyle(root).getPropertyValue(varName).trim();

    if (color) {
      this.webApp.setHeaderColor(color);
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const webApp = window.Telegram?.WebApp;

  if (!webApp) {
    console.warn("Telegram.WebApp not found");
    return;
  }

  const tgHelper = new TelegramAppHelper(webApp);
  tgHelper.setHeaderColorFromVar('--main_purple');

});

