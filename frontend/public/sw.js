self.addEventListener('push', event => {
  const data  = event.data?.json() || {};
  const title = data.title || 'Email Manager Agent';
  const body  = data.body  || 'You have new notifications';
  const url   = data.url   || '/jobs';

  event.waitUntil(
    self.registration.showNotification(title, {
      body,
      icon:  '/vite.svg',
      badge: '/vite.svg',
      data:  { url },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});
