const { createApp, ref, computed, watch, nextTick } = Vue;
const STORAGE_KEY = "screenshot-review-state";
const COMMENTS_KEY = "screenshot-review-comments";

// REVIEW_DATA is loaded via <script src="screenshot-data.js"> in the HTML

function parseProjectPath(fullPath) {
  if (!fullPath) return { repo: "", worktree: "" };
  // Check for .worktrees pattern: /path/to/repo/.worktrees/worktree-name
  const wtMatch = fullPath.match(/^(.+?)\/\.worktrees\/(.+?)$/);
  if (wtMatch) {
    const repoPath = wtMatch[1];
    const repoName = repoPath.split("/").pop();
    return { repo: repoName, worktree: wtMatch[2] };
  }
  // Just the directory name
  return { repo: fullPath.split("/").pop(), worktree: "" };
}

createApp({
  setup() {
    const data = ref(REVIEW_DATA);
    const colorMode = ref(data.value.screenshots[0]?.modes?.[0] || "dark");
    const activeFilter = ref("all");
    const viewMode = ref("list");
    const lightboxIndex = ref(null);
    const lightboxEl = ref(null);

    // Reviews: { key: "pass" | "issue" | null }
    let savedReviews = {};
    try {
      const r = localStorage.getItem(STORAGE_KEY);
      if (r) savedReviews = JSON.parse(r);
    } catch (e) {
      // ignore
    }
    const reviews = ref(savedReviews);
    watch(
      reviews,
      (v) => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(v));
      },
      { deep: true },
    );

    // Comments: { key: "comment text" }
    let savedComments = {};
    try {
      const c = localStorage.getItem(COMMENTS_KEY);
      if (c) savedComments = JSON.parse(c);
    } catch (e) {
      // ignore
    }
    const comments = ref(savedComments);
    watch(
      comments,
      (v) => {
        localStorage.setItem(COMMENTS_KEY, JSON.stringify(v));
      },
      { deep: true },
    );

    // Batch selection for multi-issue commenting
    const selected = ref(new Set());
    const batchComment = ref("");

    const components = computed(() => [
      ...new Set(data.value.screenshots.map((s) => s.component)),
    ]);
    const allModes = computed(() => [
      ...new Set(data.value.screenshots.flatMap((s) => s.modes)),
    ]);

    const showIssuesOnly = ref(false);

    const filtered = computed(() => {
      let list = data.value.screenshots.filter((s) =>
        s.modes.includes(colorMode.value),
      );
      if (activeFilter.value !== "all") {
        list = list.filter((s) => s.component === activeFilter.value);
      }
      if (showIssuesOnly.value) {
        list = list.filter((s) => reviews.value[reviewKey(s)] === "issue");
      }
      return list;
    });

    const filteredComponents = computed(() => {
      if (activeFilter.value === "all") return components.value;
      return [activeFilter.value];
    });

    function setFilter(f) {
      activeFilter.value = f;
      const url = new URL(window.location);
      if (f === "all") url.searchParams.delete("component");
      else url.searchParams.set("component", f);
      history.replaceState(null, "", url);
    }

    function hasMode(m) {
      return allModes.value.includes(m);
    }
    function countByComponent(c) {
      return data.value.screenshots.filter((s) => s.component === c).length;
    }
    function screenshotsByComponent(c) {
      return filtered.value.filter((s) => s.component === c);
    }
    function globalIndex(s) {
      return filtered.value.indexOf(s);
    }
    function reviewKey(s) {
      return `${s.component}/${s.variant}`;
    }

    function imgPath(s) {
      const base = data.value.screenshotBaseDir || ".";
      return `${base}/${s.component}.__screenshots__/${colorMode.value}/${s.variant}.png`;
    }

    function imgStyle(s) {
      const style = {};
      if (s.contentAspectRatio) {
        style.aspectRatio = `${s.contentAspectRatio}`;
      }
      if (data.value.borderInset) {
        style.clipPath = "inset(1px)";
      }
      return style;
    }

    function openLightbox(i) {
      lightboxIndex.value = i;
      nextTick(() => {
        if (lightboxEl.value) lightboxEl.value.focus();
      });
    }
    function prevLightbox() {
      if (lightboxIndex.value > 0) lightboxIndex.value--;
    }
    function nextLightbox() {
      if (lightboxIndex.value < filtered.value.length - 1)
        lightboxIndex.value++;
    }

    function toggleReview(key, status, event) {
      if (status === "issue" && event && (event.metaKey || event.ctrlKey)) {
        // Cmd+click: add to batch selection
        reviews.value[key] = "issue";
        const s = new Set(selected.value);
        if (s.has(key)) {
          s.delete(key);
        } else {
          s.add(key);
        }
        selected.value = s;
        return;
      }

      if (status === "issue") {
        if (reviews.value[key] === "issue") {
          // Toggling off: clear review, comment, and selection
          reviews.value[key] = null;
          delete comments.value[key];
          const s = new Set(selected.value);
          s.delete(key);
          selected.value = s;
        } else {
          reviews.value[key] = "issue";
        }
      } else {
        // Pass toggle
        reviews.value[key] = reviews.value[key] === status ? null : status;
        if (status === "pass") {
          delete comments.value[key];
          const s = new Set(selected.value);
          s.delete(key);
          selected.value = s;
        }
      }
    }

    function updateComment(key, text) {
      if (text) {
        comments.value[key] = text;
      } else {
        delete comments.value[key];
      }
    }

    function applyBatchComment() {
      const text = batchComment.value.trim();
      if (!text) return;
      for (const key of selected.value) {
        comments.value[key] = text;
      }
      selected.value = new Set();
      batchComment.value = "";
    }

    const hasAnyReviews = computed(
      () => Object.keys(reviews.value).length > 0,
    );

    function clearAllReviews() {
      reviews.value = {};
      comments.value = {};
      selected.value = new Set();
    }

    function cancelBatch() {
      selected.value = new Set();
      batchComment.value = "";
    }

    function isSelected(key) {
      return selected.value.has(key);
    }

    function selectedCount() {
      return selected.value.size;
    }

    function cosmosUrl(s) {
      if (!data.value.cosmosBaseUrl || !s.fixturePath) return null;
      // Cosmos expects paths relative to the package root (e.g., src/components/Foo.fixture.tsx)
      // Strip the screenshotBaseDir prefix if it's a parent of the fixture path
      let fixturePath = s.fixturePath;
      const base = data.value.screenshotBaseDir;
      if (base) {
        // Walk up from screenshotBaseDir to find the src/ ancestor
        const parts = base.split("/");
        const srcIdx = parts.indexOf("src");
        if (srcIdx > 0) {
          const prefix = parts.slice(0, srcIdx).join("/") + "/";
          if (fixturePath.startsWith(prefix)) {
            fixturePath = fixturePath.slice(prefix.length);
          }
        }
      }
      const fixture = { path: fixturePath };
      if (s.displayName) fixture.name = s.displayName;
      return `${data.value.cosmosBaseUrl}/?fixture=${encodeURIComponent(JSON.stringify(fixture))}`;
    }

    // Build a prompt from all issues for pasting into AI
    const issueEntries = computed(() => {
      return data.value.screenshots.filter(
        (s) => reviews.value[reviewKey(s)] === "issue",
      );
    });

    // Auto-disable issues filter when no issues remain
    watch(issueEntries, (entries) => {
      if (entries.length === 0) {
        showIssuesOnly.value = false;
      }
    });

    function buildPrompt() {
      const issues = issueEntries.value;
      if (issues.length === 0) return "";
      const base = data.value.screenshotBaseDir || ".";
      const lines = [
        "Fix the following visual issues found during screenshot review:",
        "",
        `COMPONENT_ROOT = ${base}`,
        "Note: all paths below are relative to COMPONENT_ROOT",
        "",
      ];
      for (const s of issues) {
        const key = reviewKey(s);
        const comment = comments.value[key];
        const variant = s.displayName || s.variant;
        const fixture = s.fixturePath
          ? s.fixturePath.replace(base + "/", "")
          : "";
        lines.push(`- **${s.component}** — variant "${variant}"`);
        if (fixture) {
          lines.push(`Fixture: ${fixture}`);
        }
        if (comment) {
          lines.push(`Issue: ${comment}`);
        }
        const modes = s.modes.length > 1 ? `{${s.modes.join(",")}}` : s.modes[0];
        lines.push(
          `Screenshots: ${s.component}.__screenshots__/${modes}/${s.variant}.png`,
        );
        lines.push("");
      }
      return lines.join("\n");
    }

    const showPromptPreview = ref(false);

    function togglePromptPreview() {
      showPromptPreview.value = !showPromptPreview.value;
    }

    function copyPrompt() {
      const text = buildPrompt();
      if (!text) return;
      navigator.clipboard.writeText(text);
      promptCopied.value = true;
      setTimeout(() => {
        promptCopied.value = false;
      }, 2000);
    }

    const promptCopied = ref(false);
    const pathCopied = ref(false);
    const projectInfo = computed(() => parseProjectPath(data.value.projectPath));

    function copyPath() {
      navigator.clipboard.writeText(data.value.projectPath || "");
      pathCopied.value = true;
      setTimeout(() => {
        pathCopied.value = false;
      }, 2000);
    }

    // Apply theme class to #app (can't use :class on mount element)
    const appEl = document.getElementById("app");
    watch(
      colorMode,
      (mode) => {
        appEl.className = `theme-${mode}`;
      },
      { immediate: true },
    );

    // Restore URL state
    const urlComponent = new URLSearchParams(window.location.search).get(
      "component",
    );
    if (urlComponent && components.value.includes(urlComponent))
      activeFilter.value = urlComponent;

    return {
      data,
      colorMode,
      activeFilter,
      viewMode,
      lightboxIndex,
      lightboxEl,
      reviews,
      comments,
      selected,
      batchComment,
      components,
      filtered,
      filteredComponents,
      allModes,
      hasMode,
      imgPath,
      imgStyle,
      reviewKey,
      cosmosUrl,
      setFilter,
      countByComponent,
      screenshotsByComponent,
      globalIndex,
      openLightbox,
      prevLightbox,
      nextLightbox,
      toggleReview,
      updateComment,
      applyBatchComment,
      cancelBatch,
      isSelected,
      selectedCount,
      issueEntries,
      buildPrompt,
      copyPrompt,
      promptCopied,
      hasAnyReviews,
      clearAllReviews,
      copyPath,
      pathCopied,
      projectInfo,
      showIssuesOnly,
      showPromptPreview,
      togglePromptPreview,
    };
  },
}).mount("#app");
