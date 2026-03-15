---
name: claude-playground-enhanced
description: Use when building playgrounds with tabbed navigation, deploy plans, step workflows, markdown content, or persistent user state. Enhances the base playground:playground skill.
---

# Enhanced Playground Patterns

Patterns for playgrounds that go beyond simple control panels — tabbed navigation, deploy plans, markdown content, persistent state.

**REQUIRED:** Use `playground:playground` first for core requirements and template selection. This skill layers on top.

## URL State with replaceState

Sync meaningful view state to the URL so shared links land on the right thing. Use `replaceState` (not `pushState`) to avoid polluting browser history.

```javascript
// On tab click, option select, section toggle — any navigation-like action
const url = new URL(window.location);
url.searchParams.set('tab', tab);
history.replaceState(null, '', url);
```

On init, read params and activate:

```javascript
const urlTab = new URLSearchParams(window.location.search).get('tab');
if (urlTab) {
  const btn = [...document.querySelectorAll('.nav button')].find(b =>
    b.dataset.tab?.replace(/-/g, '').toLowerCase() === urlTab.replace(/-/g, '').toLowerCase()
  );
  if (btn) btn.click();
}
```

Applies to tabs, selected cards, diagram variants, path toggles — anything someone might share via URL.

## localStorage Persistence

Persist user state (comments, checkboxes, document edits) across refresh. One namespaced key per concern.

```javascript
const STORAGE_KEY = 'my-playground-deploy';
function load() {
  try { const r = localStorage.getItem(STORAGE_KEY); if (r) return JSON.parse(r); } catch(e) {}
  return { comments: {}, done: {} };
}
function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ comments: state.comments, done: state.done }));
}
```

Call `persist()` on every mutation. Load before first render. Large editable documents get their own key.

## Application Framework: Vue 3 (Global Build)

For any playground with meaningful interactivity (reactive state, filters, bidirectional navigation, computed outputs), use **Vue 3's global build** via CDN. This is the standard framework for playgrounds — it provides reactive state management, computed properties, and clean component structure without any build step.

```html
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
```

Use the **Composition API** (`ref`, `computed`, `watch`) inside a single `createApp`. Keep all state as reactive refs — filters, selections, user input, view modes. Use `computed` for derived values (filtered lists, generated prompts). Use `watch` for side effects (scrolling, localStorage persistence).

```javascript
const { createApp, ref, computed, watch, nextTick, onMounted } = Vue;

createApp({
  setup() {
    const items = ref([...]);
    const activeFilter = ref('all');
    const filtered = computed(() =>
      activeFilter.value === 'all' ? items.value : items.value.filter(i => i.type === activeFilter.value)
    );
    // ... return all refs and computed for template use
    return { items, activeFilter, filtered };
  }
}).mount('#app');
```

**Why Vue 3:** Excellent AI training data (fewer mistakes), familiar to React users (Composition API mirrors hooks), works with zero tooling from CDN, handles complex state cleanly. Preferred over Alpine.js (weaker AI support, messy at scale) and Petite Vue (unmaintained).

## Markdown Rendering with marked.js + highlight.js

**Exception to the base skill's "no external dependencies" rule.** For markdown-heavy playgrounds, hand-rolled regex breaks on nested lists, tables, and fenced code. Use marked.js for parsing + highlight.js with `github-dark` theme for syntax highlighting.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/github-dark.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11/lib/core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11/lib/languages/bash.min.js"></script>
<script>
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value;
    return hljs.highlightAuto(code).value;
  }
});
</script>
```

**Strip YAML frontmatter before rendering.** marked.js doesn't understand `---` delimited frontmatter — it renders it as raw text or a broken `<hr>`. Before passing markdown to `marked.parse()`, strip it:

```javascript
function stripFrontmatter(md) {
  const match = md.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return { content: md, frontmatter: null };
  const raw = match[1];
  const meta = Object.fromEntries(
    raw.split('\n').filter(l => l.includes(':')).map(l => {
      const [k, ...v] = l.split(':');
      return [k.trim(), v.join(':').trim().replace(/^["']|["']$/g, '')];
    })
  );
  return { content: md.slice(match[0].length), frontmatter: meta };
}
```

Optionally render extracted frontmatter as a styled metadata bar above the document (title, status, owner, etc.) — or hide it entirely. In Code view, show the raw frontmatter with a muted style to distinguish it from document content.

**You must style the output container.** marked.js produces unstyled HTML. Without these, code blocks are unreadable:

```css
.md-content pre { background: #0d1117; border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 18px; overflow-x: auto; }
.md-content pre code { background: none; padding: 0; color: #c9d1d9; font-size: 13px; line-height: 1.6; white-space: pre; }
.md-content blockquote { border-left: 3px solid var(--accent); padding: 10px 16px; background: rgba(88,166,255,0.06); }
.md-content blockquote p { margin-bottom: 0; }
.md-content th, .md-content td { border: 1px solid var(--border); padding: 8px 12px; }
.md-content th { background: var(--surface2); font-weight: 600; }
```

## Bidirectional Navigation Pattern

For playgrounds with linked panels (e.g., document + annotations, code + issues), implement bidirectional click-to-scroll navigation:

```javascript
const activeFocusId = ref(null);

function focusItem(id, panelSelector) {
  activeFocusId.value = id;
  nextTick(() => {
    const el = document.querySelector(`[data-id="${id}"]`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('focus-highlight');
      setTimeout(() => {
        el.classList.remove('focus-highlight');
        activeFocusId.value = null;
      }, 2000);
    }
  });
}
```

Use a temporary gold pulse animation that's visually distinct from static highlighting:

```css
@keyframes focus-pulse {
  0% { box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.8); background: rgba(255, 215, 0, 0.25); }
  100% { box-shadow: 0 0 0 0 transparent; background: transparent; }
}
.focus-highlight { animation: focus-pulse 2s ease-out forwards; }
```

## Document View Modes

For document-heavy playgrounds, provide a view mode toggle (Preview / Code / Split):

- **Preview**: Rendered markdown via `marked.js` with styled tables, code blocks, blockquotes
- **Code**: Raw source with line numbers, optional line-level annotations (colored borders, click targets)
- **Split**: Code left + preview right, scroll-synced

## UX Rules

- **Content inside tabs, not above them.** Floating content above the tab bar creates visual disconnection.
- **Expand steps by default.** Users collapse what they don't need — don't make them click 12 times.
- **One big textarea > split form fields.** For documents (decision logs, specs), a single markdown textarea with live preview. Users think in documents, not forms.
- **Kill useless buttons.** If a button's action is unclear or redundant, remove it.
- **Visually distinguish incomplete items.** `.not-deployed { opacity: 0.7 }` with gray dots instead of green for "written but not deployed" vs "done".

## Deploy Plan Steps

For step-by-step deploy/setup plans, store steps as data with `title`, `resource`, and `md` (full markdown):

- Render markdown per step via `marked.parse(step.md)`
- Copy button per step (copies raw markdown)
- Comment button per step (persisted to localStorage)
- Done checkbox per step (persisted to localStorage)
- Resource inventory table auto-generated from step data
- Hide duplicate heading if step markdown starts with `### Title` matching the header: `.step-body .md-content > h3:first-child { display: none; }`
