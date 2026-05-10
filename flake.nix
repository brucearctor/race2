{
  description = "race2 — OBD-II vehicle data logger";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          name = "race2";

          packages = with pkgs; [
            # Python toolchain
            python312
            uv

            # Git tooling
            git
            lefthook

            # Linting / formatting
            ruff

            # Utilities
            jq
            just
          ];

          shellHook = ''
            echo "🏎️  race2 dev shell"
            echo "   uv sync   → install deps"
            echo "   just      → list tasks"

            # Ensure uv venv is active
            if [ -f pyproject.toml ] && [ ! -d .venv ]; then
              uv sync
            fi

            if [ -d .venv ]; then
              source .venv/bin/activate
            fi

            # Install lefthook hooks on first enter
            if [ -f lefthook.yml ] && command -v lefthook &>/dev/null; then
              lefthook install -f 2>/dev/null || true
            fi
          '';
        };
      });
}
