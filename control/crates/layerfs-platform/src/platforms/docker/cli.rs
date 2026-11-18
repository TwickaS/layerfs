//! One `docker` CLI call on the machine's Engine socket, as today's
//! `platform/docker/index.js` `socketRun` makes it.
use crate::error::MachineError;
use crate::probe::first_line;
use crate::setup::tool;
use crate::spec::Spec;
use std::process::Command;

/// `docker -H unix://<socket> args...`.
pub(super) fn docker(spec: &Spec, args: &[&str]) -> Result<Command, MachineError> {
    let mut command = tool::command(&spec.tools, &tool::find(&spec.tools, "docker")?, ["-H"]);
    command
        .arg(format!("unix://{}", spec.tools.docker_socket.display()))
        .args(args);
    Ok(command)
}

/// Whether a Linux host's worker shares the host's network. It does not unless
/// `LAYERFS_DOCKER_HOST_NETWORK` is set: a host-network container is outside
/// Docker's network isolation and, on Docker Desktop, the VM's network rather
/// than the host's. The worker otherwise publishes its port on the host's
/// loopback, as on macOS.
pub(super) fn host_network() -> bool {
    cfg!(target_os = "linux") && std::env::var_os("LAYERFS_DOCKER_HOST_NETWORK").is_some()
}

/// The Engine's version, when it answers.
pub(super) fn engine_version(spec: &Spec) -> Option<String> {
    let command = docker(spec, &["version", "--format", "{{.Server.Version}}"]).ok()?;
    first_line(command, false)
}
