{
    description = "";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs";
    inputs.flake-utils.url = "github:numtide/flake-utils";
    outputs = {self, nixpkgs, flake-utils}:
      flake-utils.lib.eachDefaultSystem(system:
        let
          overrides = pkgs: {
            fdfgen = pkgs.fdfgen.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or []) ++ [pkgs.setuptools];
            });
            pyhafas = pkgs.pyhafas.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or []) ++ [pkgs.setuptools];
            });
            django-bootstrap4 = pkgs.django-bootstrap4.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or []) ++ [pkgs.hatchling];
            });
            contourpy = pkgs.contourpy.override {
              preferWheel = true;
            };
          };
          overlay = final: prev: {
            fahrplandatengarten-app = prev.poetry2nix.mkPoetryApplication {
              projectDir = ./.;
              overrides = prev.poetry2nix.defaultPoetryOverrides.extend (self: super: (overrides super));
            };
            fahrplandatengarten = final.fahrplandatengarten-app.dependencyEnv;
          };
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ overlay ];
          };
        in {
          defaultPackage = pkgs.fahrplandatengarten;
          packages = { inherit (pkgs) fahrplandatengarten; };
          devShells.default = (pkgs.poetry2nix.mkPoetryEnv {
            projectDir = ./.;
            editablePackageSources = {
              fahrplandatengarten = ./fahrplandatengarten;
            };
            overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: (overrides super));
          }).env;
        }
      );
}

