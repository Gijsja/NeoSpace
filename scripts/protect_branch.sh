#!/bin/bash
# Protects the master branch using GitHub API
# Requires 'admin' scope token

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "🛡️  Protecting branch 'master' for $REPO..."

gh api -X PUT "repos/$REPO/branches/master/protection" \
  -f required_status_checks.strict=true \
  -f required_status_checks.contexts[]=test \
  -f required_status_checks.contexts[]=lint \
  -f enforce_admins=true \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f required_pull_request_reviews.require_code_owner_reviews=true \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f restrictions=null

echo "✅ Branch protection enabled!"
