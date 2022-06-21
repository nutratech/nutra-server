import subprocess  # nosec


def release_git_parse() -> tuple:
    """Gets release info by calling git commands"""

    def git_cmd(args: str):
        return (
            subprocess.run(args.split(), capture_output=True, check=True)  # nosec
            .stdout.decode()
            .rstrip()
        )

    try:
        git_sha = git_cmd("git rev-parse --short HEAD")
        git_commit_date = git_cmd("git show -s --format=%ci")

        return (
            git_sha,
            git_commit_date,
        )

    except KeyError as err:
        print(f"WARN: {repr(err)}")
        return None, None
