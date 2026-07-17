# Cow Memory Hindsight fork

This branch is the Cow-owned Hindsight engine boundary. Its upstream base is `92f433c90409636804c0797071a4abbe141f76c5` (`v0.8.4`). Cow Memory pins the resulting Cow commit as a Git submodule and builds API-only, local-model-only, immutable multi-architecture images from that exact tree.

## Rules

- `origin` must be `https://github.com/cow-ai/hindsight.git`.
- `upstream` must be `https://github.com/vectorize-io/hindsight.git`.
- Never force-push a pinned Cow commit.
- Never publish `latest` or a mutable production tag.
- Never enable cloud LLM, embedding, or reranker fallback.
- Never expose the API or control plane directly to clients.
- Never run startup migrations with runtime credentials.
- Every patch records its upstream base, schema/API effect, compatibility evidence, license impact, and upstreaming status.

Run `cow-memory/check-fork.sh` before pushing. The parent Cow Memory repository owns deployment, Gateway policy, credentials, journaling, authority, and client access; this fork owns only Hindsight engine source and image construction.
