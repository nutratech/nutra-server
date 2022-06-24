import subprocess  # nosec


def release_git_parse() -> tuple:
    """Gets release info by calling git commands"""

    def git_cmd(args: str):
        try:
            return (
                subprocess.run(args.split(), capture_output=True, check=True)  # nosec
                .stdout.decode()
                .rstrip()
            )
        except subprocess.CalledProcessError as sp_err:
            print(f"WARN: Git command error: {repr(sp_err)}")
            return None

    git_sha = git_cmd("git rev-parse --short HEAD") or "UNKNOWN"
    git_commit_date = git_cmd("git show -s --format=%ci") or "1970-01-01"

    return (
        git_sha,
        git_commit_date,
    )
