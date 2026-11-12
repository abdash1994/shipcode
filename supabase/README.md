# ShipCode backend (Supabase project "ShipCode", ref ljcusofcvjnrrojxsicw)

Applied as migration `shipcode_sync_proofs_events`.

- `states`: one row of saved progress per signed-in learner. Row-level security: a learner can read and write only their own row.
- `proofs`: public proof pages. No direct access; `publish_proof`, `unpublish_proof`, `my_proof` (signed-in only) and `get_proof(slug)` (anyone with the link).
- `events`: opt-in anonymous usage events. Anyone may insert; nobody can read them through the API. Read them in the Supabase dashboard.

The key in `index.html` is the public "anon" key. It is meant to be public; the rules above are what protect the data.

## One-time dashboard setup (required for sign-in emails)
Authentication > URL Configuration:
- Site URL: `https://shipcode-30.vercel.app`
- Redirect URLs: add `https://shipcode-30.vercel.app/**`

Without this, the emailed sign-in link sends people to `localhost:3000`.

## Known limits
- Supabase's built-in email sender is rate-limited and meant for testing. For more than a handful of sign-ups an hour, connect your own email provider (Authentication > Emails > SMTP).
- Settings > Delete account calls the `delete_my_account()` function (security definer, signed-in users only), which removes the auth user and, through cascades, their progress and proof page. Verify it against your project before relying on it: the app's tests use a fake server.
- Password sign-up needs Authentication > Providers > Email enabled. If "Confirm email" is on, new users must open the emailed link first. Turn on leaked-password protection (Authentication > Policies) in the dashboard; the app only enforces 8+ characters locally.
- Sync happens when the app opens and when progress changes. Two devices open at once: the newest save wins.
