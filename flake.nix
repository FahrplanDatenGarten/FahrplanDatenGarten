{
    description = "";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs";
    inputs.flake-utils.url = "github:numtide/flake-utils";
    outputs = {self, nixpkgs, flake-utils}:
        flake-utils.lib.eachDefaultSystem(system:
        let pkgs = nixpkgs.legacyPackages.${system}; in {
            devShells.default = (pkgs.poetry2nix.mkPoetryEnv {
                projectDir = ./.;
                editablePackageSources = {
                    fahrplandatengarten = ./FahrplanDatenGarten;
                };
                overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: {
                    fdfgen = super.fdfgen.overridePythonAttrs (old: {
                        buildInputs = (old.buildInputs or []) ++ [super.setuptools];
                    });
                    pyhafas = super.pyhafas.overridePythonAttrs (old: {
                        buildInputs = (old.buildInputs or []) ++ [super.setuptools];
                    });
                    django-bootstrap4 = super.django-bootstrap4.overridePythonAttrs (old: {
                        buildInputs = (old.buildInputs or []) ++ [super.hatchling];
                    });
                    contourpy = super.contourpy.override {
                      preferWheel = true;
                    };
                });
            }).env;
        });
}

