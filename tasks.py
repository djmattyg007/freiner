import os
import sys

from invoke import task, util


pty = util.isatty(sys.stdout) and util.isatty(sys.stderr)


@task
def reformat(c):
    c.run("isort freiner tests setup.py tasks.py", pty=pty)
    c.run("black freiner tests setup.py tasks.py doc/source/conf.py", pty=pty)


@task
def lint(c):
    c.run("flake8 --show-source --statistics --max-line-length 100 freiner tests", pty=pty)
    c.run("check-manifest", pty=pty)


@task
def test(c, onefile=""):
    pytest_args = ["pytest", "--cov=freiner", "--cov-branch", "--cov-report=term"]
    if os.environ.get("CI", "false") == "true":
        pytest_args.append("--cov-report=xml")
        _pty = False
    else:
        pytest_args.append("--cov-report=html")
        _pty = pty

    if onefile:
        pytest_args.append(onefile)

    c.run("docker-compose down --remove-orphans --volumes", pty=_pty)
    c.run("docker-compose up -d", pty=_pty)
    try:
        c.run(" ".join(pytest_args), pty=_pty)
    finally:
        c.run("docker-compose down --remove-orphans --volumes", pty=_pty)

        c.run("rm .docker/memcached/freiner.memcached.sock", pty=_pty, warn=True)
        c.run("rm .docker/redis/freiner.redis.sock", pty=_pty, warn=True)

@task
def type_check(c):
    c.run("mypy freiner tests", pty=pty)
