#!/bin/sh
# One-time: make git stamp sw.js automatically before each commit.
printf '#!/bin/sh\npython3 tools/release.py && git add sw.js\n' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit && echo "pre-commit hook installed"
