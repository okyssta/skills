# Inline JS in Server-Rendered Templates

Pitfalls when embedding JavaScript directly inside a Jinja2/Flask template (`<script>` tag in `.html` file).

## Backslash Escaping in Regex Literals

**Problem:** Writing `/^\/compare\/?/` in a `.html` template works in a standalone `.js` file, but the same content inside a Jinja2 template gets extra escaping. Each `\/` in the template becomes `\\/` in the rendered HTML, which breaks the JS regex.

**Root cause:** Both the template file's content and the HTML parser's treatment of `<script>` are at play — but the most common cause is accidentally passing double-escaped content through `write_file` or a string literal that gets JSON-decoded twice.

**Fix:** Verify the *rendered HTML* contains exactly `/^\/compare\/?/` (single `\` before each `/`), not `\\/`. Check with:
```
grep -c '\\\\/' templates/example.html  # should be 0 (no double backslashes)
hexdump -C to confirm raw bytes: 0x5c 0x2f = `\/`
```

## IIFE Closure Scope in Inline Event Handlers

**Problem:** Functions defined inside `(function(){...})()` IIFE are not accessible from `onclick="sel(event)"` attribute handlers because those run in global scope.

**Fix:** Use event delegation on a container element instead of inline `onclick`:

```js
r.addEventListener('click', function(e) {
  var t = e.target.closest('[data-action]');
  if (!t) return;
  // handle selection
});
```

This keeps the handler inside the IIFE closure where it can access private variables.

## Template-Generated HTML Strings Inside JS

When a JS function builds HTML strings (via `innerHTML = ...`), the rendered template contains `</` sequences that the HTML parser might interpret as closing the parent `<script>` tag. Avoid embedding `</` inside JS string literals by using `<\/` or breaking the sequence (e.g., `'<' + '/div>'`).

**Safer pattern:** generate a template element or use `document.createElement` instead of `innerHTML` strings when the content includes HTML tags with closing brackets.

## Validation Checklist

Before declaring JS-in-template work done:

1. **Render the page** via curl and extract the inline `<script>` content.
2. **Syntax-check** the extracted JS with `node --check`.
3. **Test the API calls** the JS depends on with curl.
4. **Verify no `\\`** where `\` is intended in regex literals.
5. **Verify no `</script>`** appears inside the script body.
