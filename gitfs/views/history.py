from datetime import datetime
from errno import ENOENT
from stat import S_IFDIR
from pygit2 import GIT_SORT_TIME

from gitfs import   FuseOSError
from log import log
from .view import View


class HistoryView(View):
    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        if path != '/':
            raise FuseOSError(ENOENT)
        return dict(st_mode=(S_IFDIR | 0755), st_nlink=2)


    def opendir(self, path):
        return 0

    def releasedir(self, path, fi):
        pass

    def access(self, path, amode):
        log.info('%s %s', path, amode)
        return 0

    def _get_commits_by_date(self, date):
        """
        Retrieves all the commits from a particular date.

        :param date: date with the format: yyyy-mm-dd
        :type date: str
        :returns: a list containg the commits for that day. Each list item
            will have the format: hh:mm:ss-<short_sha1>, where short_sha1 is
            the short sha1 of the commit.
        :rtype: list
        """

        date = datetime.strptime(date, '%Y-%m-%d').date()
        commits = []
        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TIME):
            commit_time = datetime.fromtimestamp(commit.commit_time)
            if  commit_time.date() == date:
                time = commit_time.time().strftime('%H-%m-%S')
                commits.append("%s-%s" % (time, commit.hex[:7]))

        return commits

    def readdir(self, path, fh):
        commits = self._get_commits_by_date(self.date)
        dir_entries = ['.', '..'] + commits

        for entry in dir_entries:
            yield entry
