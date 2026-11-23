# The worker container's seccomp profile

`worker.json` is Docker's own default seccomp profile plus exactly one change:
`pivot_root` is added to the syscalls allowed under `CAP_SYS_ADMIN`. The Sandbox
helper (`layerfs-sandbox-helper`, `mounts.rs`) pivots into each Sandbox's root, and
Docker's default filter answers `EPERM` to `pivot_root`. The worker has
`CAP_SYS_ADMIN` (not `--privileged`), so the call is allowed only with that
capability, as `mount` and `unshare` are.

- `moby-default.json`: moby/moby `vendor/github.com/moby/profiles/seccomp/default.json`
  at commit `70efc0e31da3a115fc87574d1b786fa2b867c346` (tag `docker-v29.9.3`),
  sha256 `785b2429264afba4d594320337cb17f144f3c7d51585f9805eef72e28f4f9334`.
  Source: https://github.com/moby/moby/blob/70efc0e31da3a115fc87574d1b786fa2b867c346/vendor/github.com/moby/profiles/seccomp/default.json
- `worker.json`: the file `power.rs` writes to the machine's folder and passes as
  `--security-opt seccomp=<file>`.
- `tools/check_worker_seccomp.py` checks the recorded sha256 of the original and that
  `worker.json` is it with exactly that one name added.

To follow a newer Docker, replace `moby-default.json` with the new profile, update the
commit and sha256 here and in the script, regenerate `worker.json`, and run the check.
