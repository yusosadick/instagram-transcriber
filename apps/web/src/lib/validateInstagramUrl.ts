const INSTAGRAM_URL_PATTERN =
  /^https?:\/\/(www\.|m\.)?instagram\.com\/(reel|reels|p|tv)\/[A-Za-z0-9_-]+\/?(\?.*)?$/;

export function isInstagramUrl(source: string): boolean {
  return INSTAGRAM_URL_PATTERN.test(source.trim());
}
