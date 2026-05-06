{
  description = "AbitAssistant Bot - Telegram bot for university admission assistance";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python313;

        pythonPackages = python.pkgs;

      in
      {
        devShells.default = pkgs.mkShell {
          name = "abitassistant-bot-dev";

          packages = with pkgs; [
            # Python
            python
            pythonPackages.pip
            pythonPackages.uv

            # Docker
            docker
            docker-buildx
            docker-compose

            # Linting & formatting
            ruff

            # Utilities
            git
            jq
            curl
          ];

          shellHook = ''
            echo "AbitAssistant Bot development environment"
            echo "Python: $(python --version)"
            echo ""
            echo "Available commands:"
            echo "  make docker-up      - Start containers"
            echo "  make docker-down    - Stop containers"
            echo "  make docker-logs    - View container logs"
            echo "  make docker-restart - Restart containers"
            echo "  make lint           - Run ruff lintelr"
            echo "  make format         - Format code with ruff"
            echo ""
          '';
        };
      }
    );
}
