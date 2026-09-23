# Derived dev image for p2-HUB75-LED-Matrix-Driver.
#
# Bakes the network-heavy installs that previously ran in postCreateCommand on
# EVERY container create (pnut-ts compiler + Claude CLI) into cached layers, so
# rebuilds are cheap and offline.
#
# No apt packages are installed: the base image already provides unzip/curl, and
# image-tools-mcp no longer needs libtesseract5 at runtime (removed 2026-07-04).
FROM mcr.microsoft.com/devcontainers/javascript-node:24-bookworm

# --- git: workspace trust + baked identity -----------------------------------
# The workspace arrives over a virtiofs bind mount whose uid attribution is
# occasionally transient -- the same path can report uid 1000 one moment and a
# different uid the next with nothing changed on disk. Git's ownership check
# then refuses with "detected dubious ownership" and every git query in the tree
# fails. Intermittently, which is worse than always: it makes gates that
# discover their inputs with `git ls-files` report green having read nothing.
#
# Scoped to /workspaces/* rather than '*' so the check stays live elsewhere.
# A trailing /* matches at any depth.
RUN git config --system --add safe.directory '/workspaces/*'

# Identity is BAKED here rather than bind-mounted from the host's ~/.gitconfig.
#
# A single-FILE bind mount pins the source inode. macOS rewrites ~/.gitconfig by
# rename -- `git config --global` does, and so does every editor's atomic save --
# which produces a NEW inode, leaving the container's mount pointed at the old
# unlinked one. The container then reads frozen content until it is recreated.
# That is the "stale .gitconfig" failure; it stranded the fleet on 2026-08-28 and
# cleared only on reboot. The other host mounts (.ssh, .claude, container-tools)
# are DIRECTORIES and are immune, because each lookup inside them resolves fresh.
# .gitconfig was the fleet's only single-file mount. Retired 2026-09-10.
#
# Only the portable subset is baked. The host config's remaining blocks are
# macOS-only and are inert or harmful under Linux: credential.helper=osxkeychain
# (no such helper here -- VS Code installs its own, below); filter.lfs and
# filter.media with required=true (neither binary is installed, which is a hard
# checkout failure in any repo that tracks LFS paths); the UltraCompare merge and
# difftool under /Applications; and a safe.directory for a /Users/stephen path
# that does not exist in a container.
#
# System scope, not --global: --global writes ~/.gitconfig, which is
# container-local and does not survive a rebuild. /etc/gitconfig is root-owned,
# baked, and does. VS Code appends its credential helper to the same file at
# container start; the two coexist.
RUN git config --system user.name 'Stephen M Moraco' \
    && git config --system user.email 'stephen@ironsheep.biz' \
    && git config --system push.default simple \
    && git config --system push.followTags false \
    && git config --system pull.rebase false

# --- ...AND THE SYSTEM CONFIG MUST BE THE ONE THAT ACTUALLY WINS -------------
#
# ⛔ THE BLOCK ABOVE WAS SHADOWED AND INERT FROM THE DAY IT WAS WRITTEN.
# Retiring the ~/.gitconfig bind mount (Inconsistency W) did NOT stop the host's
# file from reaching this container: the VS Code Dev Containers extension COPIES
# the host ~/.gitconfig in at container start. Different mechanism, same result.
# MEASURED 2026-09-11 in P2-uSD-FAT32-FS -- PID 1 at 20:29:37, /etc/gitconfig
# rewritten at :38.23 (VS Code adding its credential helper), ~/.gitconfig
# written at :40.36. Three seconds after boot, every boot.
#
# Git precedence is system < global < local, so that copied GLOBAL file
# outranked everything baked above. The identity was right only by COINCIDENCE
# -- both files carry the same name and email -- which is exactly why nobody
# noticed. The comment above described a mechanism that was not in force.
#
# AND THE COPY IS NOT MERELY REDUNDANT, IT IS ARMED. It carries filter.lfs and
# filter.media at required=true with NEITHER BINARY INSTALLED. That is a hard
# checkout failure the moment any .gitattributes routes a path through them --
# not hypothetical: MEASURED LIVE 2026-09-11 in the workspace-root container,
# "git-lfs: not found" / "fatal: the remote end hung up unexpectedly" on a
# tracked path. It also carries an UltraCompare merge/difftool under
# /Applications and an alias pointing at ~/bin/, neither of which exists here.
#
# THE FIX RELOCATES "GLOBAL"; IT DOES NOT DELETE THE COPY. Deleting the copy in
# a start hook would RACE the copy, and a fix whose correctness depends on
# unproven ordering is not a fix. GIT_CONFIG_GLOBAL (git >= 2.32) names the
# global file outright: git then reads ONLY that path as global and ignores
# ~/.gitconfig entirely. The copy still lands and is simply never read.
# Deterministic, no race. The variable is set in devcontainer.json
# `containerEnv` so it reaches EVERY process -- not just login shells, which is
# why this is not done in .bashrc.
#
# ⭐ NOTHING IS LOST, AND THAT WAS VERIFIED RATHER THAN ASSUMED. Every live
# setting in the copied file is byte-identical in /etc/gitconfig: user.name,
# user.email, push.default, push.followTags, pull.rebase -- and VS Code writes
# its credential helper to BOTH, so HTTPS auth is unaffected. What the
# relocation drops is precisely the dead and harmful blocks named above.
#
# The file is created HERE (not left to git) so it exists, is user-owned and
# writable: a `git config --global ...` still succeeds and lands somewhere
# container-local and harmless, instead of silently re-shadowing the bake.
RUN mkdir -p /home/node/.config/git \
    && printf '%s\n' \
       '# Container-local GLOBAL git config.' \
       '#' \
       '# GIT_CONFIG_GLOBAL points here (devcontainer.json containerEnv) so that' \
       '# the host ~/.gitconfig, which the VS Code Dev Containers extension copies' \
       '# into this container at every start, is IGNORED rather than shadowing the' \
       '# identity baked into /etc/gitconfig. Put container-only overrides here;' \
       '# keeping it empty is the preference.' \
       > /home/node/.config/git/config \
    && chown -R node:node /home/node/.config

# --- pnut-ts compiler --------------------------------------------------------
# *** THE VERSION IS DISCOVERED, NOT TYPED. ***
# It used to be spelled out in three places -- the COPY, the cp path and the rm --
# so dropping a newer zip in and rebuilding silently rebuilt the OLD compiler,
# with nothing anywhere reporting which one you got. The glob takes every zip
# present and the sort picks the highest version, so adding a zip is the whole
# upgrade. The chosen version is echoed into the build log, and `pnut-ts
# --version` is run as a build-time smoke test so a bad binary fails the layer
# rather than the first compile that needs it.
#
# NOTE: the zip baked here is linux-arm64 (Apple Silicon host). Re-point the
# COPY glob if building on an x64 host.
COPY pnut-ts-linux-arm64-*.zip /tmp/pnut/
RUN cd /tmp/pnut \
    && ZIP="$(ls pnut-ts-linux-arm64-*.zip | sort -V | tail -1)" \
    && echo "Baking pnut-ts from ${ZIP}" \
    && unzip -oq "$ZIP" \
    && cp "${ZIP%.zip}/pnut_ts/pnut-ts" /usr/local/bin/pnut-ts \
    && chmod +x /usr/local/bin/pnut-ts \
    && mkdir -p /opt/pnut-ts-docs \
    && find "${ZIP%.zip}/pnut_ts" -maxdepth 1 -type f \
         ! -name 'pnut-ts' ! -name 'pnut_ts' -exec cp {} /opt/pnut-ts-docs/ \; \
    && cd / && rm -rf /tmp/pnut \
    && pnut-ts --version

# --- Claude CLI (was: curl | bash in postCreateCommand) ----------------------
# Installed as the `node` user so it lands in /home/node/.local/bin.
USER node
RUN curl -fsSL https://claude.ai/install.sh | bash \
    && grep -q '\.local/bin' ~/.bashrc 2>/dev/null \
       || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
USER root
