{
    description = "";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs";
    inputs.flake-utils.url = "github:numtide/flake-utils";
    outputs = {self, nixpkgs, flake-utils}: let
      # this is ugly, we should move the overrides to a more top position
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
    in {
      overlay = final: prev: {
        fahrplandatengarten = prev.poetry2nix.mkPoetryApplication {
          projectDir = self;
          overrides = prev.poetry2nix.defaultPoetryOverrides.extend (self: super: (overrides super));
        };
      };
    } // flake-utils.lib.eachDefaultSystem(system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
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
      in {
        defaultPackage = pkgs.fahrplandatengarten;
        packages = { inherit (pkgs) fahrplandatengarten; };
        devShell = (pkgs.poetry2nix.mkPoetryEnv {
          projectDir = self;
          editablePackageSources = {
            fahrplandatengarten = ./fahrplandatengarten;
          };
          overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: (overrides super));
        }).env;
      }
    );
}

