import { useNotifications } from '../context/NotificationContext'

export function useNotificationDemo() {
  const { addNotification } = useNotifications()

  const showSuccessNotification = (title: string, message: string) => {
    addNotification({
      type: 'success',
      title,
      message,
      priority: 'medium',
      autoDismiss: true,
      dismissTimeout: 3000
    })
  }

  const showErrorNotification = (title: string, message: string) => {
    addNotification({
      type: 'error',
      title,
      message,
      priority: 'high',
      autoDismiss: false
    })
  }

  const showWarningNotification = (title: string, message: string) => {
    addNotification({
      type: 'warning',
      title,
      message,
      priority: 'medium',
      autoDismiss: true,
      dismissTimeout: 5000
    })
  }

  const showInfoNotification = (title: string, message: string) => {
    addNotification({
      type: 'info',
      title,
      message,
      priority: 'low',
      autoDismiss: true,
      dismissTimeout: 4000
    })
  }

  const showSystemNotification = (title: string, message: string) => {
    addNotification({
      type: 'system',
      title,
      message,
      priority: 'medium',
      autoDismiss: true,
      dismissTimeout: 6000
    })
  }

  const showUrgentNotification = (title: string, message: string, action?: { label: string; onClick: () => void }) => {
    addNotification({
      type: 'error',
      title,
      message,
      priority: 'urgent',
      autoDismiss: false,
      action
    })
  }

  const showArchivalComplete = (archiveName: string) => {
    showSuccessNotification(
      'Archival Complete',
      `Archive "${archiveName}" has been successfully created and stored.`
    )
  }

  const showArchivalError = (error: string) => {
    showErrorNotification(
      'Archival Failed',
      `Failed to create archive: ${error}`
    )
  }

  const showTTLExpiry = (itemName: string, expiryDate: Date) => {
    showWarningNotification(
      'TTL Expiry Warning',
      `Item "${itemName}" will expire on ${expiryDate.toLocaleDateString()}`
    )
  }

  const showBlockchainTransaction = (txHash: string) => {
    showInfoNotification(
      'Blockchain Transaction',
      `Transaction ${txHash.slice(0, 10)}... has been confirmed`
    )
  }

  return {
    showSuccessNotification,
    showErrorNotification,
    showWarningNotification,
    showInfoNotification,
    showSystemNotification,
    showUrgentNotification,
    showArchivalComplete,
    showArchivalError,
    showTTLExpiry,
    showBlockchainTransaction
  }
}
