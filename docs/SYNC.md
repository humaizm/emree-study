# Free online sync — Firebase setup (5 minutes, $0 forever)

The app already syncs **portably for free**: Export file, Import, and Copy-link
(resume links carry all 120 answers + flags in the URL hash, which never leaves
the browser). Those need no account and can never break.

This page adds the **automatic** layer: progress follows the user across devices
with zero clicks, via Firebase's free Spark plan. Why Firebase and not a custom
server or Cloudflare Workers:

- Anonymous auth + Firestore rules = per-user isolated storage with **no
  middleware code to host, patch, or pay for**.
- Spark plan needs **no credit card**. Free quota: 1 GB stored, 50k reads +
  20k writes/day. This quiz writes ~5 KB per change (debounced 2s) — hundreds
  of daily users fit comfortably.
- Supabase free was rejected (projects pause after 7 idle days); a paused
  database is the opposite of durable.

## What only you can do (Google login required — nothing here is automatable)

### 1. Create the project (2 min)

1. Open console.firebase.google.com → **Add project**.
2. Name it `emree-sync` (any name works). Decline Google Analytics.
3. No billing step appears on the Spark plan. If anything asks for a card, stop —
   you clicked the wrong plan.

### 2. Register the web app (1 min)

1. Project home → `</>` **Add an app** → nickname `emree-web`.
2. Copy the 7 `firebaseConfig` values.

### 3. Paste the config (1 min)

Open `site-config.js` in this repo and fill the `firebase:` object, e.g.:

```js
window.EMREE_CONFIG = { firebase: {
  apiKey: "AIza…", authDomain: "emree-sync.firebaseapp.com",
  projectId: "emree-sync", storageBucket: "emree-sync.appspot.com",
  messagingSenderId: "123456789012", appId: "1:123456789012:web:abcdef…" } };
```

Commit + push. No rebuild needed — the file is served as-is. Keys are public
by design; the rules below are the actual security.

### 4. Enable Anonymous auth (30 sec)

Build → Authentication → Sign-in method → **Anonymous** → Enable → Save.

### 5. Create the database + paste the rules (1 min)

Build → Firestore Database → **Create database** → Production mode → region
closest to users (e.g. `eur3` / `asia-south1`) → Enable. Then the **Rules** tab:
delete everything, paste the full contents of `firestore.rules` from this repo,
**Publish**. The console validates syntax on publish — a green banner means the
contract (narrow collection, schema + size caps, server timestamp, deny-all
elsewhere) is live.

## How sync behaves (implemented in `index.html`)

- Offline-first: browser storage stays primary; Firestore is the roaming copy.
- On answer: local save immediately, cloud push debounced 2 s.
- On launch / tab refocus: pull once; if the cloud copy is newer (>5 s), it wins
  and the save line says so. Newest timestamp always wins — predictable, no
  silent merges.
- Devices are linked by a 16-char key (`Key: XXXX-…` in the deck). Same key on
  two devices = same record. Keys are unguessable; losing yours just starts a
  fresh record (nothing breaks).
- Offline: status reads "offline — changes kept on this device" and everything
  keeps working. Sync resumes on reconnect.

## Cost and abuse notes (read before sharing widely)

- Free quota resets daily; exceeding it fails reads/writes until reset — the app
  degrades to local-only, it never loses data.
-   Worst case abuse (someone spamming writes) burns daily quota, not money —
  Spark cannot bill you. If that ever happens: enable **App Check** (free,
  console → App Check → register the web app with reCAPTCHA v3, then flip
  Firestore to enforced mode) and ask an agent to wire `firebase-appcheck-compat.js`
  + `activate()` into the sync loader — a 15-minute job, documented procedure.
- Never commit service-account keys. The web config above is the only secret
  this project will ever hold, and it is safe to publish.

## Verify it worked

1. Answer 2 questions on your phone → deck reads "Sync: on · saved HH:MM:SS".
2. Open the site on a laptop → same 2 answers appear within seconds.
3. DevTools → Application → IndexedDB/LocalStorage untouched by us; the
   `progress/{your-key}` document in the Firebase console shows your data.
