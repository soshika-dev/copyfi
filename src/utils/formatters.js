const dateTimeFormatter = new Intl.DateTimeFormat('fa-IR', {
  dateStyle: 'medium',
  timeStyle: 'short'
})

export function formatFaDate(dateValue) {
  if (!dateValue) return '-'
  const date = new Date(dateValue)
  if (Number.isNaN(date.getTime())) return '-'
  return dateTimeFormatter.format(date)
}

export function toSnippet(text, limit = 140) {
  if (!text) return ''
  return text.length > limit ? `${text.slice(0, limit)}...` : text
}
