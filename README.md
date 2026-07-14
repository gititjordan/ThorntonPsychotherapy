# Thornton Psychotherapy & Wellness Website

Updated:
- Larger, centered logo on mobile
- Square logo image added for link previews/social sharing
- Open Graph and Twitter preview meta tags added
- Favicon/apple touch icon added

Note: Some apps cache link previews. After deploying, iMessage/Facebook may need time or a cache refresh before showing the new image.
# Thornton Psychotherapy & Wellness

Static website deployment package.

## Publish checklist

Upload the entire project structure—not the HTML files by themselves:

- `index.html`
- `about.html`
- `privacy.html`
- `accessibility.html`
- `assets/` and every file inside it
- `robots.txt`
- `sitemap.xml`

After deployment, verify these paths return successfully:

- `/assets/site-logo-760.png`
- `/assets/gladys-photo-900.jpg`
- `/assets/psychology-today-verified.png`
- `/assets/social-preview.jpg`

The Calendly booking iframe loads eagerly when the page opens, with early connection hints in the page head.
