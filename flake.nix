{
  description = "Environment to package a tauri app.";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/3a9b551601446eb20f028b9ae3397709666d9387";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.rust-overlay.url = "github:oxalica/rust-overlay";
  inputs.tauri-driver.url = "github:tauri-apps/tauri";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };
  inputs.tauri-driver.flake = false;

  outputs = {
    self,
    nixpkgs,
    rust-overlay,
    flake-utils,
    tauri-driver,
    poetry2nix,
    ...
  }:
    flake-utils.lib.eachSystem
    ["x86_64-linux"]
    (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          (import rust-overlay)
        ];
      };
      inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;
      node = pkgs.nodejs-16_x;
      libraries = with pkgs; [
        webkitgtk
        gtk3
        cairo
        gdk-pixbuf
        glib
        dbus
        openssl_3

        xorg.libX11
        sqlite
      ];

      packages = with pkgs;
        [
          rust-bin.stable.latest.default
          curl
          wget
          pkg-config
          libsoup

          python311
          poetry2nix.packages.${system}.poetry
          nodejs-18_x

          # Language servers
          rnix-lsp
          alejandra
          rust-analyzer
          nodePackages.svelte-language-server
          nodePackages.typescript-language-server
          nodePackages.eslint_d
        ]
        ++ libraries;
    in {
      packages = {
        yark = mkPoetryApplication {
          projectDir = ./yark;
          python = pkgs.python311;
        };
        yark-api = mkPoetryApplication {
          projectDir = ./yark-api;
          python = pkgs.python311;
        };
        yark-cli = mkPoetryApplication {
          projectDir = ./yark-cli;
          python = pkgs.python311;
        };
        default = self.packages.${system}.yark-cli;
      };

      devShell = pkgs.mkShell {
        buildInputs = packages;

        shellHook = ''
          export OPENSSL_DIR="${pkgs.openssl.dev}"
          export OPENSSL_LIB_DIR="${pkgs.openssl.out}/lib"

          export WEBKIT_DISABLE_COMPOSITING_MODE=1
          export GIO_MODULE_DIR=${pkgs.glib-networking}/lib/gio/modules/
          export PATH=".extra:$PATH"
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath libraries}:$LD_LIBRARY_PATH
        '';
      };
    });
}
