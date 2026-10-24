# Browser topology and safe setup

## Discovery before installation

Use available browser-tool schemas or the repository's existing Playwright
dependency first. Check OS/WSL, the requested desktop, tool versions, executable
paths and an explicitly approved test-browser connection. Do not search a home
directory or personal browser profile for an authenticated session.

If tooling is missing, an authorized browser-test request can justify installing
the missing driver/browser in a session-local tooling directory. Do not change
application manifests merely to run an ad hoc acceptance test. Follow the host's
package-install and execution rules; missing native dependencies do not authorize
system-wide installs, execution-policy overrides, firewall changes or auth bypass.

## WSL and Windows Edge

A headed browser launched inside WSL or a container is not necessarily visible on
the Windows desktop. Probe Windows browser/app reachability from Windows, not
only from Linux loopback. Inspect documented interop commands and resolve paths
with `wslpath` when available; never hardcode a distribution or user profile path.

Prefer the installed Windows Edge with a new dedicated temporary profile. Launch
it only under operator authorization, with an unused loopback debugging port,
`--user-data-dir` pointing to an owned test directory, and no first-run/default
browser prompts where supported. Remote debugging provides browser control:
never expose it publicly or attach it to the operator's ordinary browser.

Use Playwright's supported `channel: "msedge"` when browser and driver share a
Windows runtime. If attaching across tools, `connectOverCDP` must target the
explicitly approved test endpoint. CDP has lower fidelity than Playwright's
native connection; disclose limitations rather than assuming feature parity.

Example after the operator-approved endpoint has been established:

```js
import { chromium } from "playwright";

const endpoint = process.env.TEST_BROWSER_CDP_ENDPOINT;
if (!endpoint) throw new Error("Explicit test-browser endpoint required");
const url = new URL(endpoint);
if (url.protocol !== "http:" ||
    !["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)) {
  throw new Error("Use an approved loopback endpoint");
}
const browser = await chromium.connectOverCDP(endpoint);
const context = browser.contexts()[0];
if (!context) throw new Error("No approved test context");
const ownedPage = await context.newPage();
// Exercise only the approved application journey.
await ownedPage.close();
// Do not close an operator-owned browser as test cleanup.
```

Discover Windows Node/Playwright availability rather than assuming the Linux
installation is executable there. If portable tooling is needed, keep it in an
owned temporary directory and use official distributions with checksum
verification. Normal local-file execution may avoid UNC-path authorization
issues, but never change or bypass execution policy to make a blocked script run.
If normal local execution is also blocked, stop and request operator setup.

Use a fresh test session with normal GitHub sign-in. Never read credentials,
cookies, browser storage or authentication caches to automate login. A visible
sign-in request should be reported immediately, not after a long silent timeout.

## Process ownership and isolation

Record test-browser/driver process ownership and tool handles. Keep temporary
helpers bounded; leave a browser accessible between turns only when necessary
for an explicitly requested sign-in or operator inspection. Never use global
name-based process killing. A virtual-display/viewer is an optional fallback,
not the default; protect it with authentication and loopback binding.

A temporary container can isolate browser dependencies without host changes.
Keep app source, credentials and personal profiles unmounted. Verify viewer
WebSocket/canvas connectivity as well as HTTP readiness; neither proves app
authentication or acceptance.

## Upstream references

Recheck host/version-specific behavior against primary documentation:

- Playwright browser installation and branded channels: `playwright.dev/docs/browsers`.
- Playwright `BrowserType.connectOverCDP`: `playwright.dev/docs/api/class-browsertype`.
- Microsoft WSL networking: `learn.microsoft.com/windows/wsl/networking`.
- Copilot skill discovery: official GitHub Copilot CLI skills documentation.

These are discovery pointers, not permission to upload source or private evidence.
