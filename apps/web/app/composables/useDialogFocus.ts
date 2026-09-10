import { nextTick, onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

const FOCUSABLE_SELECTOR = [
  'button:not([disabled])',
  'a[href]',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

export interface DialogFocusController {
  dialogRef: Ref<HTMLElement | null>
  onDialogKeydown(event: KeyboardEvent): void
}

export function useDialogFocus(onClose: () => void): DialogFocusController {
  const dialogRef = ref<HTMLElement | null>(null)
  let opener: HTMLElement | null = null
  let shell: HTMLElement | null = null

  function focusableElements(): HTMLElement[] {
    return dialogRef.value
      ? Array.from(dialogRef.value.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
        .filter(element => !element.hasAttribute('disabled') && element.getAttribute('aria-hidden') !== 'true')
      : []
  }

  function onDialogKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      event.preventDefault()
      onClose()
      return
    }
    if (event.key !== 'Tab') return

    const focusable = focusableElements()
    if (!focusable.length) {
      event.preventDefault()
      dialogRef.value?.focus()
      return
    }

    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }

  onMounted(async () => {
    opener = document.activeElement instanceof HTMLElement ? document.activeElement : null
    shell = document.querySelector<HTMLElement>('[data-testid="case-shell"]')
    shell?.setAttribute('inert', '')
    await nextTick()
    const focusable = focusableElements()
    ;(focusable[0] ?? dialogRef.value)?.focus()
  })

  onBeforeUnmount(() => {
    shell?.removeAttribute('inert')
    opener?.focus()
  })

  return { dialogRef, onDialogKeydown }
}
