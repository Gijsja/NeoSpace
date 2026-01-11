#!/bin/bash
# Protects the master branch using GitHub API
# Requires 'admin' scope token

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "🛡️  Protecting branch 'master' for $REPO..."

# Construct JSON payload ensuring booleans are actual booleans, not strings
cat > protection_payload.json <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "test",
      "lint"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF

# Send request with explicit JSON input
gh api -X PUT "repos/$REPO/branches/master/protection" --input protection_payload.json

# Cleanup
rm protection_payload.json

echo "✅ Branch protection enabled!"
