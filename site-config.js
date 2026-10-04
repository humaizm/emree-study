/* EMREE Question Bank - optional online sync config.
 *
 * Firebase web keys are PUBLIC BY DESIGN. Security lives in firestore.rules,
 * not in these values - there is nothing secret here.
 *
 * Until this is filled in, the app works fully offline-first
 * (browser storage + export file + resume link). Nothing breaks.
 *
 * Free 5-minute setup (no billing, no credit card) - see docs/SYNC.md:
 *   1. console.firebase.google.com -> Add project -> Add a Web app
 *   2. Paste the 7 values below (this file is served as-is, no rebuild needed)
 *   3. Authentication -> Sign-in method -> enable Anonymous
 *   4. Firestore Database -> Create database -> paste in firestore.rules
 */
window.EMREE_CONFIG = { firebase: null };
/* Example when configured:
window.EMREE_CONFIG = { firebase: {
  apiKey: "AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "emree-sync.firebaseapp.com",
  projectId: "emree-sync",
  storageBucket: "emree-sync.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
} };
*/
