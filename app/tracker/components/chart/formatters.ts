export const formatTimestamp = (() => {
    let lastDay: number | null = null;
    let tickCounter = 0;
  
    return (timestamp: number): string => {
      const date = new Date(timestamp * 1000);
      const day = date.getDate();
  
      if (lastDay !== day) {
        lastDay = day;
        tickCounter = 0;
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        });
      }
  
      tickCounter++;
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: tickCounter % 2 !== 0,
      });
    };
  })();
  
  export const formatCrosshairTime = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };
  