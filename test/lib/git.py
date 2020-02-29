import downloads
import json
import os
import re


def update_version_file(version_file):
    with open(version_file) as f:
        version = json.load(f)

    with open(version_file, "w") as f:
        current = version["next"]
        version_pattern_rex = "(anthoscli-.+-rc)(\\d+)"
        m = re.match(version_pattern_rex, current)
        next = re.sub(version_pattern_rex, m.group(1) + str(int(m.group(2)) + 1),
                  current)
        new_version = {"current": current, "next": next}
        f.write(json.dumps(new_version, indent=2))
    return current


class Git(object):
    def __init__(self, repo, target, version_file, env=None):
        if env is None:
            env = os.environ.copy()
        self.bin = "git"
        self.env = env
        downloads.exec(["chmod", "600", "/root/.ssh/id_rsa"])
        downloads.exec(["git", "config", "--global", "user.email", "anthos-blueprints-validation-bot@google.com"])
        downloads.exec(["git", "config", "--global", "user.name", "anthos-blueprints-validation-bot"])
        downloads.exec(["git", "clone", repo, target])
        self.statedir = target
        self.version_file = target + "/" + version_file

    def __repr__(self):
        return "Git:" + downloads.exec(["which", "git"])

    def update_version(self, tag, branch):
        self.exec(["checkout", tag])
        new_tag = update_version_file(self.version_file)
        self.exec(["add", self.version_file])
        self.exec(["commit", "-m", "Update the anthoscli release version to " + new_tag])
        self.exec(["push", "origin", "HEAD:%s" % branch])
        return new_tag

    def create_remote_tag(self, tag):
        self.exec(["tag", tag])
        self.exec(["push", "origin", tag])

    def exec(self, args):
        return downloads.exec(
            [self.bin] + args, cwd=self.statedir, env=self.env
        ).strip()
