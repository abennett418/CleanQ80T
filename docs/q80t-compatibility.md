# CleanQ80T compatibility audit

Repository audit: 24 October 2026. CleanQ80T is a fork of CleanFrame 0.6.1.
No TV connection, installation, launch or settings change was performed.

## Target and evidence

The owner supplied model QA65Q80TAWXXY and firmware release 2743.0.
The complete software string remains in the conversation; no private device
identifiers or network details are needed in this document.

Samsung documents 2020 TVs as Tizen 5.5 with Chromium M69. This is our porting
baseline, not a readback from this TV. Firmware 2743.0 is not a Tizen version.
The upstream evidence in tv-status.md describes a different, Tizen 9 Frame TV.
It must not be read as CleanQ80T installation or compatibility evidence.

Sources:
- https://developer.samsung.com/smarttv/develop/specifications/general-specifications.html
- https://developer.samsung.com/smarttv/develop/specifications/web-engine-specifications.html

## Audit findings before adaptation

1. **Package minimum prevents a 5.5 install.** app/config.xml declares
   required_version="6.5". Lower it only with the runtime adaptations and checks;
   changing this declaration alone does not establish compatibility.
2. **Flex spacing needs replacement.** app/style.css uses flexbox gap for Home
   controls, buttons, editor rows and appearance choices. Chrome added flex gap
   in 84; M69 will omit the spacing. Replace with direction-aware child margins,
   accounting for row-reverse, column layout and hidden elements. CSS.supports
   for gap alone is insufficient because older Chrome supports grid gap.
3. **Positioning shorthand needs replacement.** inset:0 occurs on materials,
   tile contents, native icons and the appearance overlay. Chrome added inset
   in 87. Use explicit top/right/bottom/left declarations so layers retain their
   intended coverage. Preserve cached material geometry.
4. **Keyboard outline enhancement is newer.** :focus-visible requires Chrome
   86. The existing .is-focus remote styling is independent, so this is not a
   launcher-blocking issue. Review a :focus fallback during browser adaptation.
5. **Core APIs are plausible on 5.5.** device.js uses application.launch,
   getAppsInfo, ApplicationControl and launchAppControl. These public API
   contracts predate 5.5; launch/discovery still require actual device evidence.
   main.js uses ES5-style syntax, Promise-based font loading, localStorage,
   canvas text measurement, visibility events and requestAnimationFrame. No
   obvious newer-JavaScript syntax blocker was found by source inspection;
   the current Node syntax check is not an ES5 validator.
6. **Frame controls are not portable.** Art Mode launches org.tizen.art-app
   using an undocumented Frame contract. Do not present this as Q80T Art Mode
   support. Hide or capability-gate it for this target. Samsung Home and TV
   settings also have fixed reference-TV IDs; verify destinations independently.
   The current failure text suggesting Home returns to CleanFrame also assumes
   a remapping that has not happened on this TV.
7. **App discovery retains reference assumptions.** Default streaming IDs are
   repeated in main.js and device.js. The catalogue excludes some Samsung/system
   apps and the alternate YouTube ID. Discover Q80T IDs before promising specific
   shortcuts; preserve saved order and migrations when adapting the catalogue.
8. **Identity and tooling need an independent setup.** The manifest, device
   self-filter and scripts/check.py retain nClrkHome1.FrameHome. Before signing
   this owner's build, generate their own identity and certificates and update
   these references consistently. scripts/package.py is a macOS reference setup,
   not a Linux installer. Review scripts/tv.py before any device task.
9. **Native Home is a separate investigation.** The helper targets net6.0 and
   reference-device assumptions. It is not a verified Tizen 5.5 tool. Do not run
   even its query stage without an explicit device task. Home/startup writes
   require separate authority and an exact-value private recovery baseline.

Compatibility references:
- https://github.com/mdn/browser-compat-data/blob/main/css/properties/gap.json
- https://github.com/mdn/browser-compat-data/blob/main/css/properties/inset.json
- https://github.com/mdn/browser-compat-data/blob/main/css/selectors/focus-visible.json
- https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html

## Implementation sequence

1. Adapt flex spacing and positioning for M69, retaining the current appearance,
   remote navigation, storage migrations and offline rendering. Add a focused
   compatibility guard to prevent reintroducing those unsupported declarations.
2. Gate Frame-only controls and remove assumptions about a remapped physical
   Home button. Keep unavailable device controls honest in browser previews.
3. Prepare the independent CleanQ80T identity and 5.5 manifest together with
   updated assertions and self-filtering; keep signing secrets ignored.
4. Run source/public checks and public-font browser checks at 1920x1080 and
   1280x720. Modern Chromium passing is regression evidence, not M69 emulation.
5. In a separately authorised installation task, inspect Linux SDK/signing
   prerequisites, obtain actual capabilities and app IDs, install and manually
   launch, then have the owner confirm appearance and remote behaviour.
6. Investigate Home/startup only after the manually opened app works.

## Validation

- npm run check: passed on the unchanged application.
- npm run check:public: passed; no private font binaries present locally.
- CLEANFRAME_PUBLIC_FONTS=1 npm run check:browser: 344 checks passed, zero failures
  in modern Chromium, after installing the missing Playwright Chromium binary.
- No M69 runtime, Q80T rendering, app launch, Art/Ambient destination or native
  Home compatibility has been established by this audit.

The software-engineer skill's referenced base skill and engineering documents
were absent from this environment; repository guidance and the available skill
were used. That limitation applied to the initial audit; the adaptation below updates the app.

## Adapted version

The first Q80T port candidate replaces flex gap with direction-aware sibling
margins, expands inset into explicit sides, and uses a focus outline supported
by M69. Frame Art Mode is removed from Home and the adapter. Error text no longer
promises that the physical Home button returns to this launcher.

The app is named CleanQ80T, package CQ80T4f92a, application CQ80T4f92a.Home, with
required_version 5.5. Manifest assertions, device self-filter, browser fixtures
and native helper target agree. The native helper's original model/firmware
guards remain; it is not ported or approved for this TV. Existing storage keys
and migrations remain intact. No signing certificates were created or reused.

Development-only Acorn enforces ES5 parsing across packaged JavaScript. CSS
checks reject gap/inset and focus-visible. These are focused regression guards,
not an exhaustive engine compatibility validator. Browser tests cover the two
remaining Home controls and their remote navigation, spacing with icons/text,
and overlay sizing at both target resolutions, plus the upstream behaviour
suite. All Samsung/streaming IDs remain candidates until checked on this TV.

TV installation, actual engine readback, destination verification and native
Home work remain separate future stages.

Adaptation validation: `npm run check`, `npm run check:public` and
`CLEANFRAME_PUBLIC_FONTS=1 npm run check:browser` passed. The final browser run
completed 406 checks with zero failures, including both target resolutions.
List and Dock were also inspected in the public-font collaborative preview.
The ES5 parser was checked to reject newer syntax. No device was contacted,
no signed widget was built, and no Home/startup settings were changed.

## First Q80T device inspection

On 24 October 2026, the owner enabled Developer Mode and explicitly authorised
SDB capability and installed-app-list reads. The connection succeeded.
Capabilities report `platform_version:5.5`, `cpu_arch:armv7`, `profile_name:tv`.
This confirms the Tizen baseline and architecture; the web-engine version has
not been read directly. Addresses and raw diagnostics remain ignored locally.

The installed-app list includes the expected primary IDs for Netflix, YouTube,
Disney+, Prime Video, Apple TV, ABC iview and SBS On Demand. It also includes
BINGE, Stan, Kayo, Spotify, Tubi, Hayu and 7plus. Stremio and Apple Music were not
listed as installed apps and should not be initial shortcuts for this setup.
App-list presence is not proof of a successful or visible app launch.

No apps were installed or launched and no Home/startup values were read or
changed in this inspection. Signing, installation and physical verification
remain pending.

Initial Home defaults now use the nine selected video services: Netflix,
YouTube, Disney+, Prime Video, Apple TV, ABC iview, SBS On Demand, BINGE and
Stan. Sport services, Tubi, Hayu and 7plus are excluded from the initial Home
selection; no installed apps were removed. Spotify remains accessible through
All apps. Existing saved Home choices remain intact. BINGE and Stan use initials
or discovered native icons because bundled logos are not provided.

After this selection change, source validation and all 411 public-font browser
checks passed. Browser launch checks use mocked Tizen calls; actual TV launches
remain untested.

## First installation and launch

With explicit owner approval, the official SDK installed the independently
signed CleanQ80T 0.6.1 widget on the Q80T. The installer reported completion and
the installed-app list confirmed `CQ80T4f92a.Home`. The launch command returned
success. Owner confirmation of visible rendering and remote behaviour remains
pending; command success alone is not visual evidence. No Home/startup settings
were changed. Signing material, device addresses and raw logs remain local.

The owner subsequently confirmed that the installation works on the TV. This
establishes visible launcher operation on the Q80T; individual shortcut results
and native Home/startup behaviour have not been separately confirmed.
