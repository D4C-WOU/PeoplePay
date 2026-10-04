/**
 * Join optional Tailwind class names without requiring another runtime package.
 *
 * PeoplePay only needs simple conditional class composition, so keeping this
 * helper local makes the UI easier to understand and maintain.
 */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
