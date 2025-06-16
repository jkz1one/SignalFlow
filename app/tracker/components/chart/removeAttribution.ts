export function removeTradingViewAttribution(): void {
    // Wait for DOM to fully mount in case chart is injected late
    setTimeout(() => {
      const logo = document.getElementById('tv-attr-logo');
      if (logo) {
        logo.remove();
      }
    }, 0);
  }
  