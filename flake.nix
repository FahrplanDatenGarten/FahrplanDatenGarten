{
    description = "";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    inputs.flake-parts.url = "github:hercules-ci/flake-parts";
    inputs.poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    outputs = inputs: inputs.flake-parts.lib.mkFlake { inputs = inputs; } {
      imports = [
        inputs.flake-parts.flakeModules.easyOverlay
      ];
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
      perSystem = { config, pkgs, self, ... }: let
        p2n = (inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; });
        overrides = prev: {
          fdfgen = prev.fdfgen.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [prev.setuptools];
          });
          pyhafas = prev.pyhafas.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [prev.setuptools];
          });
          django-bootstrap4 = prev.django-bootstrap4.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [prev.hatchling];
          });
          contourpy = prev.contourpy.override {
            preferWheel = true;
          };
        };
      in {
        overlayAttrs = {
          inherit (config.packages) fahrplandatengarten;
        };
        packages.fahrplandatengarten = p2n.mkPoetryApplication {
          projectDir = inputs.self;
          overrides = p2n.defaultPoetryOverrides.extend (final: prev: (overrides prev));
        };
        devShells.default = (p2n.mkPoetryEnv {
          projectDir = inputs.self;
          editablePackageSources = {
            fahrplandatengarten = ./fahrplandatengarten;
          };
          overrides = p2n.defaultPoetryOverrides.extend (final: prev: (overrides prev));
        }).env;
      };
    };
}

