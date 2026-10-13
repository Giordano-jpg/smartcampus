#!/bin/sh
set -e
cd "$(git rev-parse --show-toplevel)"

chmod +x hooks/pre-commit hooks/post-commit hooks/pre-push hooks/post-push
git config core.hooksPath hooks
git config alias.pushp '!f() { git push "$@" && sh hooks/post-push; }; f'

echo "Hooks instalados. Usa 'git pushp' en vez de 'git push' para ver el post-push."