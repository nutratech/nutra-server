import os

from ntserv.utils.logger import get_logger

_logger = get_logger(__name__)


def git_commit_info() -> str:
    try:
        _cwd = os.path.dirname(os.path.realpath(__name__))
        with open(os.path.join(_cwd, "git-commit-info"), encoding="utf-8") as _file:
            _git_commit_info = [_line.rstrip() for _line in _file.readlines()]
        return " ".join(_git_commit_info)

    except (FileNotFoundError, IndexError):
        _logger.debug("failed to load git-commit-info")
        return str()
