# ADR-0002: Contact workflow includes AI analysis and graceful email fallback

## Status

Accepted

## Context

The assignment requires a complete request lifecycle and at least one backend AI integration. It also requires sending an email to the site owner and a copy to the user. The service should be testable even when external providers are unavailable.

## Decision

`POST /api/contact` will process submissions as follows:

```text
validate → rate limit → AI analysis → persist submission → send/queue emails → update metrics → return 202
```

The AI feature is classification, sentiment analysis, priority, confidence, and a short owner-facing summary.

The AI provider will be OpenAI-compatible and configured with:

- `AI_API_KEY`
- `AI_BASE_URL` optional
- `AI_MODEL`, defaulting to `gpt-5.4-nano`

If AI is not configured or fails, the service uses fallback analysis:

```json
{
  "category": "unknown",
  "sentiment": "unknown",
  "summary": "AI analysis unavailable",
  "priority": "normal",
  "confidence": 0.0,
  "fallback_used": true
}
```

Email delivery uses SMTP when configured. If SMTP is unavailable or fails, messages are saved to `storage/outbox/`, and the submission is still accepted with `email_delivery = "queued"`.

## Consequences

- The API remains usable without AI or SMTP credentials, which improves local reviewability.
- The owner receives enriched notifications when AI is available.
- Email failure is not treated as contact submission failure; storage failure remains critical.
- The successful response status is `202 Accepted`, reflecting that the submission is accepted and delivery may be queued.
