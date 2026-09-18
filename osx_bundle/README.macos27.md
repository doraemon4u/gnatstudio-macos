# GNAT Studio macOS 27 / Apple Silicon bundle

This patch replaces the historical macOS packaging path with a self-contained
`GNAT Studio.app` + DMG flow suitable for the GitHub Actions `xcode-27`
ARM64 runner.

## What changed

- Uses Apple Silicon (`arm64`) in `Info.plist`.
- Raises `LSMinimumSystemVersion` to `27.0`.
- Removes the old Python 2.7 bundle step.
- Copies the active Homebrew Python 3.14 runtime plus PyGObject/PyCairo.
- Keeps a compatibility Python home at `Contents/MacOS/share/gnatstudio/python`.
- Uses `dylibbundler` to copy Homebrew / GTK / Python Mach-O dependencies into
  `Contents/Frameworks` and rewrites load commands.
- Uses an ad-hoc code signature for CI artifacts.
- Creates `GNAT-Studio-<version>-macos27-arm64.dmg` directly; no obsolete
  `pkgbuild` / `productbuild` installer is required.

## Build locally from an already-configured tree

```sh
cd osx_bundle
make dmg \
  PREFIX="$PWD/../_bundle" \
  GTK_PREFIX="$(brew --prefix gtk+3)" \
  PYTHON="python3.14"
```

The workflow performs the full dependency/toolchain setup before this step.

## Release signing / notarization

The CI build uses ad-hoc signing (`codesign --sign -`) so the artifact is
loadable for testing. A public release should replace this with Developer ID
signing and notarization, using GitHub Actions secrets / OIDC-backed signing
infrastructure appropriate for the project.
