# TypeScript Zero-Tolerance Reference

## Type Checking (tsc / tsconfig strict)

### Common Excuses and Fixes

| Error Pattern | Excuse | Fix |
|--------------|--------|-----|
| `TS2322: Type 'X' is not assignable to type 'Y'` | "The types changed upstream" | Update the call site or add a proper type assertion |
| `TS2345: Argument of type 'X' is not assignable` | "The library types are wrong" | Use a typed wrapper, not `as any` |
| `TS7006: Parameter implicitly has 'any' type` | "I'll add types later" | Add types now. `any` is never acceptable. |
| `TS2339: Property does not exist on type` | "It works at runtime" | Add the property to the type or use a type guard |
| `TS18046: 'X' is of type 'unknown'` | "I know what it is" | Narrow with a type guard, not a cast |

### Forbidden Shortcuts

- **`any`** — Never. Use `unknown` and narrow.
- **`@ts-ignore`** — Never. Fix the type error.
- **`@ts-expect-error`** — Never, unless suppressing a genuine library bug with a comment explaining the upstream issue.
- **`as` casts** — Avoid. Prefer type guards and narrowing. Only acceptable for branded types.

## Linting (Biome / ESLint)

### Common Excuses and Fixes

| Error | Excuse | Fix |
|-------|--------|-----|
| `lint/correctness/useExhaustiveDependencies` | "Adding the dep causes infinite re-renders" | Fix the dependency — use `useCallback`/`useMemo` or restructure |
| `lint/suspicious/noExplicitAny` | "The API returns any" | Type the API response with a proper interface |
| `lint/complexity/noForEach` | "forEach is fine" | Use `for...of` or `.map()` |
| Unused imports/variables | "I might need them later" | Delete them. Git has history. |
| `biome check --write` auto-fixes | "I'll format later" | Run the formatter before committing. Always. |

### biome-ignore

Only acceptable with a clear reason that references an external constraint:
```typescript
// biome-ignore lint/suspicious/noThenProperty: Required for Supabase query pattern
```

Never acceptable:
```typescript
// biome-ignore lint/correctness/useExhaustiveDependencies: too complex to fix
```

## Testing (Vitest / Jest)

### Common Excuses and Fixes

| Failure | Excuse | Fix |
|---------|--------|-----|
| `FAIL: expected X, received Y` | "The test is outdated" | Update the test to match correct behavior |
| `TypeError: Cannot read property of undefined` | "The mock is wrong" | Fix the mock setup, don't skip the test |
| Timeout failures | "The CI is slow" | Increase timeout or fix the async logic |
| Snapshot mismatch | "Just update the snapshot" | Read the diff first. Is the change intentional? |

### Forbidden Test Shortcuts

- **`test.skip()`** — Never skip a failing test. Fix it or delete it.
- **`test.todo()`** — Only for genuinely planned future tests, never to defer broken ones.
- **Disabling test files** — Commenting out imports or removing from config is never acceptable.

## Build Errors (Vite / webpack)

### Common Excuses and Fixes

| Error | Excuse | Fix |
|-------|--------|-----|
| Module not found | "It works locally" | Check import paths and package.json dependencies |
| Circular dependency | "It's too complex to untangle" | Break the cycle. Extract shared types. |
| Bundle size warnings | "Nobody checks bundle size" | Fix the import — use tree-shakeable imports |
| Type-only imports in runtime | "TypeScript strips them" | Use `import type` explicitly |
