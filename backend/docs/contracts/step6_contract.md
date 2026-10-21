# Step 6 Contract (v1)
Changes only with a heads-up in #backend

## POST /submissions
Needs `Authorization: Bearer <Clerk session token>`.

### Request Body
```json
{ "challenge_id": 1, "answer_text": "A calm beach at sunset, warm orange mood, watercolor style" }
```
- `challenge_id`: integer
- `answer_text`: string, 1–5000 characters

### Response `201`
The same shape for pass AND fail:
```json
{
  "submission_id": 12,
  "challenge_id": 1,
  "status": "needs_revision",
  "feedback": ["Your answer should mention 'mood'."],
  "xp_awarded": 0,
  "attempt_number": 2,
  "created_at": "2026-10-05T10:15:30.123456Z"
}
```

### Fields
| Field | Type | Description |
|---|---|---|
| `submission_id` | integer | Unique identifier for the submission |
| `challenge_id` | integer | Identifier of the challenge |
| `status` | string | One of `"pending" \| "passed" \| "needs_revision"` |
| `feedback` | array of strings | A list of strings, never null. On a pass it is `["Great work! Your answer meets all the requirements."]` |
| `xp_awarded` | integer | 0 unless this attempt earned XP. Only the first pass earns XP |
| `attempt_number` | integer | 1, 2, 3... per user per challenge |
| `created_at` | string | An ISO 8601 UTC string ending in `Z` |

## GET /submissions/{submission_id}
Returns one submission, same shape. 404 if it doesn't exist or isn't yours.

## GET /submissions?challenge_id=1
Returns a list of **your** submissions, newest first. `challenge_id` is optional.

## Errors
- `401`: not logged in.
- `404`: `{"detail": "Challenge not found"}` or `{"detail": "Submission not found"}`.
- `422`: the body doesn't match (FastAPI's standard error shape).

## Notes for frontend
In `api/submissionApi.ts`, the real call should:
- POST to `${process.env.NEXT_PUBLIC_API_URL}/submissions` (not `/api/submissions`);
- send the body `{ challenge_id: Number(challengeId), answer_text: answer }`;
- add the Clerk token as `Authorization: Bearer <token>`;
- map the response field `xp_awarded` to `xpEarned`. `status` and `feedback` already match `types/submission.ts`.

## Message to post
Message to post in #backend and #frontend:
"Step 6 contract v1 is in .github/backend/docs/contracts/step6_contract.md. Status values: pending / passed / needs_revision. Same response shape for pass and fail. Keep mocking until we say the endpoint is merged."
