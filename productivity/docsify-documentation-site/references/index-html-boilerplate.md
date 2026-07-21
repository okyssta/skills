# Docsify index.html Boilerplate

Minimal template for a docsify-based documentation site with a dark theme, search, copy-code, and custom brand colors.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ProjectName Documentation</title>
  <meta name="description" content="ProjectName — Short description.">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/dark.css">
  <style>
    :root { --theme-color: #8c75a5; }
    .sidebar { background: #0d1117 !important; border-right: 1px solid #21262d !important; }
    .sidebar ul li a { color: #c9d1d9 !important; }
    .sidebar ul li a:hover { color: #f46c90 !important; }
    .sidebar ul li.active > a { color: #f46c90 !important; border-right: 2px solid #f46c90; }
    .markdown-section h1 { color: #f46c90; }
    .markdown-section h2 { color: #8c75a5; }
    .markdown-section code { background: #161b22; color: #f46c90; border-radius: 4px; }
    .markdown-section pre { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
    .markdown-section th { background: #161b22; border: 1px solid #30363d; color: #8b949e; }
    .markdown-section td { border: 1px solid #30363d; }
    .cover { background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1c2333 100%) !important; }
    .cover-main h1 span { background: linear-gradient(135deg, #8c75a5, #f46c90); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  </style>
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {
      name: '<span>Project</span>Name',
      repo: 'https://github.com/user/repo',
      basePath: '/RepoName/',
      loadSidebar: true,
      coverpage: true,
      auto2top: true,
      maxLevel: 4,
      subMaxLevel: 3,
      search: { placeholder: 'Search docs...', noData: 'No results found', depth: 4 },
      plugins: [
        function(hook, vm) {
          hook.afterEach(function(html) {
            return html.replace(/\[BADGE_PAPER\]/g, '<span class="badge paper">Paper 1.21+</span>');
          });
        }
      ]
    };
  </script>
  <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/docsify.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify-copy-code@2/dist/docsify-copy-code.min.js"></script>
</body>
</html>
```

## Key Configuration Fields

| Field | Purpose | Required |
|-------|---------|----------|
| `name` | Sidebar header text | Yes |
| `repo` | GitHub corner link | Yes |
| `basePath` | GitHub Pages subpath (repo name) | Yes |
| `loadSidebar` | Enable `_sidebar.md` | Yes |
| `coverpage` | Enable `_coverpage.md` | Yes |
| `search` | Full-text search in-page | Recommended |
| `auto2top` | Scroll to top on page change | Recommended |

## Badge Pattern (Custom Plugin)

Use a custom docsify plugin for badge macros that get replaced during rendering:

```js
plugins: [
  function(hook, vm) {
    hook.afterEach(function(html) {
      return html
        .replace(/\[BADGE_PAPER\]/g, '<span class="badge paper">Paper 1.21-26.1.2</span>')
        .replace(/\[BADGE_FOLIA\]/g, '<span class="badge folia">Folia</span>')
        .replace(/\[BADGE_JAVA\]/g, '<span class="badge java">Java 21</span>')
        .replace(/\[BADGE_MIT\]/g, '<span class="badge mit">MIT</span>');
    });
  }
]
```

Then in markdown: `[BADGE_PAPER] [BADGE_FOLIA] [BADGE_JAVA] [BADGE_MIT]`
