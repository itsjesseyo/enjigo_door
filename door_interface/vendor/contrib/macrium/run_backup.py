'''
Copyright (c) 2009 by Oliver Schoenborn

Example server backup process, requiring following pre/post steps: 

1 pre: grab stdout of script to file
2 pre: warn users (via email) about server offline
3 pre: hot-backup of databases such as Trac by running tracadmin hotcopy
4 pre: shut down virtual machines
Task: do backup using Macrium Reflect
4 post: restart virtual machines
3 post: nothing to do
2 post: nothing to do
1 post: close stdout grab
5 post-only: send results (various log files) by email to admin

The system is a Win XP Pro (32 bit) system with Python 2.4 and 
Macrium Reflect installed. 

The module macriumbackups.py could be easily extended to 
support other backup systems that can be run in batch mode (ie from
command line). 

Oliver Schoenborn
Aug 2009

'''

import os, sys, time, datetime

import macriumbackups as mb


class Emailer:
    fromAddr = 'IML_Backup_Server@cpsiml.ca'
    server = 'smtp1.sympatico.ca'

    
class WarnUsers(mb.MRBackupPrePostTask, Emailer):
    '''
    Warn users that server will be down for backup.
    '''
    
    def __init__(self, delayMinutes = 5):
        self.delayMinutes = delayMinutes
        
    def executePre(self, backupTask):
        usernames = ['schoenb', 'bchawla2']
        to = [ (user+'@cae.com') for user in usernames ]
        delaySeconds = 60 * self.delayMinutes
        subject = 'WARNING: File backup of IML server in %s minutes' \
                    % self.delayMinutes
        body = '''\
        This will cause a suspension of virtual machines and other 
        databases. Commit any web-based info immediately.'''
        try:
            mb.sendMail(to, subject, body,
                fromAddr = self.fromAddr, 
                server = self.server)
            self.log('Sent warning email to %s' % ', '.join(to))
                
        except mb.SMTPServerUnreachable:
            self.log('Server unreachable, skipping step')
            
        # give users a chance to heed warning
        self.log('Waiting %s minutes so users can heed warning' 
                 % self.delayMinutes)
        time.sleep(delaySeconds)


class SendResults(mb.MRBackupPrePostTask, Emailer):
    '''
    Email the results once all done.
    '''

    def executePost(self, backupTask):
        to = ['oliver.schoenborn@gmail.com']
        success = 'successfully'
        if not backupTask.success():
            success = 'UNsucessfully'
        startTime, endTime = backupTask.getStartEndTimes()
        if endTime is None: 
            # because backupTask.endTime gets set only after all pre-post 
            # tasks have been completed. 
            endTime = datetime.datetime.now() 
        durPre, durBack, durPost = backupTask.getDurations()
        body = '''\
        The backup task "%s" has completed %s. 
        It started at %s and ended at %s. 
        Durations: pre=%s min, backup=%s min, post=%s min.''' \
            % (backupTask.getName(), success, startTime, endTime, durPre, durBack, durPost)
        subject = 'Macrium Reflect backup task completed'
        files = [fname for fname in mb.stdouts.getLogFilenames() if os.path.exists(fname)]
        self.log('Will email files %s' % files)
        try:
            mb.sendMail(to, subject, body,
                fromAddr = self.fromAddr, 
                files = files,
                server = self.server)
            self.log('Sent email with results to %s' % ', '.join(to))

        except mb.SMTPServerUnreachable:
            self.log('Server unreachable, skipping step')
            
        except IOError, exc:
            self.log(str(exc) + '; skipping it')


class TracBackups(mb.MRBackupPrePostTask):
    '''
    When doing file backups, the running Trac environments (in, say, 
    'd:\TracProjects\trac') must first be hot-copied into a backups folder
    (say, 'd:\TracProjects\backups'). The Macrium XML file includes the 
    backups folder in its definition, rather than the running Trac 
    environments. 
    '''

    def executePre(self, backupTask):
        tracFolder = r'd:\TracProjects\trac'
        destFolder = r'd:\TracProjects\backups'
        cmdPrefix = ['trac-admin', 'hotcopy']
        projects = ['HOT', 'AIMS']
        mb.stdouts.add('trac')
        
        # run all Trac hot-copies in sequence
        for project in projects:
            dest = '%s-Backup-%s' % (os.path.join(destFolder, project), datetime.datetime.now())
            cmd = cmdPrefix + [project, dest]
            try:
                job = mb.exeProc(cmd, 'trac', project)
                job.wait()
            except OSError, exc:
                self.log( str(exc) )
    
    
main = mb.Main()
#main.registerPrePostTask( mb.CaptureScriptStdout() )
main.registerPrePostTask( WarnUsers(0.1) )
main.registerPrePostTask( TracBackups() )
main.registerPrePostTask( mb.ManageVirtualBoxes() )
main.registerPostTask( SendResults() )
main()

