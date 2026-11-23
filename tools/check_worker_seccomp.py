#!/usr/bin/env python3
"""Check the docker worker's seccomp profile: moby's default profile plus `pivot_root` and nothing else.

    python3 tools/check_worker_seccomp.py
"""
import hashlib
import json
import pathlib
import sys

DIR = pathlib.Path(__file__).resolve().parent.parent / "control/crates/layerfs-platform/src/platforms/docker/seccomp"
MOBY_SHA256 = "785b2429264afba4d594320337cb17f144f3c7d51585f9805eef72e28f4f9334"
ADDED = "pivot_root"


def main() -> int:
    original_bytes = (DIR / "moby-default.json").read_bytes()
    digest = hashlib.sha256(original_bytes).hexdigest()
    if digest != MOBY_SHA256:
        print(f"moby-default.json is not the recorded profile: sha256 {digest}")
        return 1
    original = json.loads(original_bytes)
    worker = json.loads((DIR / "worker.json").read_bytes())
    if original.keys() != worker.keys():
        print("worker.json has different top-level keys")
        return 1
    for key in original:
        if key != "syscalls" and original[key] != worker[key]:
            print(f"worker.json differs in {key}")
            return 1
    if len(original["syscalls"]) != len(worker["syscalls"]):
        print("worker.json has a different number of syscall rules")
        return 1
    changed = 0
    for before, after in zip(original["syscalls"], worker["syscalls"]):
        if before == after:
            continue
        changed += 1
        if {k: v for k, v in before.items() if k != "names"} != {k: v for k, v in after.items() if k != "names"}:
            print("a changed rule differs beyond its names")
            return 1
        if after.get("includes") != {"caps": ["CAP_SYS_ADMIN"]} or after.get("action") != "SCMP_ACT_ALLOW":
            print("the changed rule is not the CAP_SYS_ADMIN allow rule")
            return 1
        if sorted(set(after["names"]) - set(before["names"])) != [ADDED] or set(before["names"]) - set(after["names"]):
            print("the changed rule adds more than " + ADDED)
            return 1
    if changed != 1:
        print(f"{changed} rules changed, expected exactly one")
        return 1
    print(f"ok: worker.json is moby's default profile ({digest[:12]}) plus {ADDED} under CAP_SYS_ADMIN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
