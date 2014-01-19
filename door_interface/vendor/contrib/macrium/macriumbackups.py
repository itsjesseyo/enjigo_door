'''
Copyright (c) 2009 by Oliver Schoenborn

Module containing helper functions and classes to execute a 
Macrium Reflect backup with pre and post tasks. It provides the 
following: 

* MRBackupTask: the main task class that represents a Macrium Reflect Backup 
* MRBackupPrePostTask (class): represent a task to be done before and/or 
  after the main backup task; this might be some setup/teardown or 
  shutdown/restart a database, etc.
* CaptureScriptStdout (class): a type of MRBackupPrePostTask to capture the 
  output of the script using this module to a file (presumably, so it can be 
  sent by email, archived, etc)
* ManageVirtualBoxes (class): a type of MRBackupPrePostTask to manage any 
  VirtualBox virtual machines, ie stop them all before the backup, and restart
  them after. 
* Main (class): a class to represent the main procedure of executing the backup 
  with all its pre and post tasks. Register one or more MRBackupPrePostTask's, 
  and call it to run the whole operation. 

In addition, various bits and pieces: 

* setReflectExe (function): change where module assumes Reflect.exe is located
* sendMail (function): to send emails, with attachments
* SMTPServerUnreachable (class): raised if sendMail fails to reach the 
  specified mail server
* exeProc (function): start a process and (optionally) capture its output to
  a file (for instance, to be emailed later using sendMail); likely useful in 
  one of your MRBackupPrePostTask's
* ExitCodes (class): contains the exit codes that can be returned to shell if error
* FatalError (class): an exception your class can raise to indicate that the operation 
  must abort the script

At the very least your script will be:

    import macriumbackups as mb
    main = mb.Main()
    main()
    
But usually it will look like this: 

    import macriumbackups as mb
    
    class SomePrePostTask(mb.MRBackupPrePostTask):
        def executePre(self, backupTask):
            ....
            mb.stdouts.add('sometask')
            mb.exeProc([...], 'sometask').wait()
            ...
            
        def executePost(self, backupTask):
            .... cleanup ...

    ...

    main = mb.Main()
    main.registerPrePostTask( SomePrePostTask() )
    ...
    main()

Last update: Sept 2009
Oliver Schoenborn

WARNING: This module is provided without any warranty as to its suitability 
for any purpose. You take total responsibility for the consequences of 
using it. 
'''
import sys, os, time
from subprocess import Popen, STDOUT, PIPE
from datetime import date, datetime


class ExitCodes:
    '''
    One of these exit codes will be returned to shell upon 
    exit from an error condition.
    '''
    UNKNOWN_CAUSE = -1
    MISSING_SCRIPT_ARG = 1
    EXEC_MR = 2
    VM_STOP_FAILED = 3


REFLECT_EXE = r'C:\Program Files\Macrium\Reflect\reflect.exe'

def setReflectExe(path):
    '''Use this to override the default path used for Macrium Reflect'''
    global REFLECT_EXE
    REFLECT_EXE = path

    
class FatalError(RuntimeError):
    '''
    Gets raised when an error occurs that would prevent progression
    to next step of backup script. The given exit code is the exit 
    code give to the OS upon exit of script. 
    '''
    
    def __init__(self, exitCode):
        self.exitCode = exitCode
        
    def __str__(self):
        return str(self.exitCode)
        

class LogFiles:
    '''
    An instance of this is created to keep track of which log files are 
    created. This is useful, for instance, so that at the end of script, 
    a message could be sent with all the files as attachments. 
    The list of files is available via getLogFilenames().
    '''
    
    CAPTURE_FILE_PREFIX = 'output-capture-'
    
    def __init__(self):
        self.captureFiles = []
    
    def add(self, filename):
        self.captureFiles.append(filename)
        
    def getLogFilenames(self):
        return [self.getLogFilename(fname) for fname in self.captureFiles]
        
    def getLogFilename(self, filename):
        '''Get the log filename for given filename'''
        return self.CAPTURE_FILE_PREFIX + filename + '.txt'
    
stdouts = LogFiles()
    

def exeProc(cmdArgs, filename=None, stdoutTag=None):
    '''Start the executable process. The cmdArgs will be given to 
    subprocess.Popen(). If filename is given, it must be a name 
    previously given to stdouts.add(filename), and a text file will be
    opened to capture the stdout and stderr of the process to the file 
    stdouts.getLogFilename(filename). IF stdoutTag is given, a "comment" 
    line containing the tag is sent to that file before the process is 
    started. The tag should therefore be representative of the process
    to be executed.
    
    The stdoutTag parameter makes it more convenient to use one file
    to grab the output of many processes (run in sequence, not in parallel
    -- otherwise file contents may be difficult to read): it will be 
    clear which process caused a given block of lines in the output file.
    For instance, 
    
        stdouts.add('vms')
        exeProc([cmd1,...], 'vms', 'vm1').wait()
        exeProc([cmd2,...], 'vms', 'vm2').wait()
        
    would use one file to capture the output of two processes, and would 
    look something like this: 
    
        ------ vm1 -------
        ... output from vm1 ...
        ------ vm2 -------
        ... output from vm2 ...
        
    NOTE that you will usually want to use this function within a 
    try-except OSError block in case the process cannot be started (not 
    found, etc).
    '''
    if filename:
        stdout = file(stdouts.getLogFilename(filename), 'a')
        if stdoutTag:
            stdout.write('------- %s -------\n' % stdoutTag)
        job = Popen(cmdArgs, stdout=stdout, stderr=STDOUT)
        stdouts.add(stdout.name)
        print '  ExeProc: Will capture stdout of "%s" to "%s"' % (cmdArgs[0], stdout.name)
        
    else: # don't capture stdout/err, just start process
        stdout = None
        job = Popen(cmdArgs)
        
    return job, stdout
    

class SMTPServerUnreachable(RuntimeError):
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)


def sendMail(to, subject, text, fromAddr="", files=[], cc=[], bcc=[], server="localhost"):
    '''This sends an email using SMTP server, with files as 
    attachments.  The code was copied almost verbatim from 
    http://www.finefrog.com/2008/05/06/sending-email-with-attachments-in-python/, 
    which seems to build on the excellent examples at 
    http://docs.python.org/library/email-examples.html.'''
    import os, smtplib, socket
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders

    assert type(to)==list
    assert type(files)==list
    assert type(cc)==list
    assert type(bcc)==list

    message = MIMEMultipart()
    message['From'] = fromAddr
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message['Cc'] = COMMASPACE.join(cc)

    message.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)

    addresses = []
    for x in to:
        addresses.append(x)
    for x in cc:
        addresses.append(x)
    for x in bcc:
        addresses.append(x)

    try:
        smtp = smtplib.SMTP(server)
    except Exception, exc:
        raise SMTPServerUnreachable(exc.args[1])
    smtp.sendmail(fromAddr, addresses, message.as_string())
    smtp.close()
    
    
class MRBackupTask:
    '''
    Represent a Macrium Reflect backup task, with pre and post tasks.
    Given the name of task, the corresponding task.xml file will be 
    used (assumed to be in same folder as script). 
    
    Typical usage would be to instantiate an MRBackupTask and call 
    its execute(). Alternately to execute(), each of its other public 
    methods can be called in succession (pre, start, monitor, 
    post, print -- which is what execute() does).
    '''
    
    def __init__(self, backupTaskName):
        # Assume this script is in same folder as the XML definition
        cmdExe = sys.argv[0]
        path = os.path.dirname(cmdExe)
        if path:
            print 'MRBackupTask: Changing CWD to "%s"' % path
            os.chdir(path)
        self.__backupTaskName = backupTaskName
        backupTaskFile = backupTaskName + ".xml"
        backupTaskFullname = '%s' % os.path.join(path, backupTaskFile)
        
        self.__backupCmd = [REFLECT_EXE, "-e", "-w", backupTaskFullname]
        self.__job = None
        self.__exitCode = None
        self.__prePostTasks = []
        self.__stdout    = None
        
        # keep track of some timings
        self.__startTime = None
        self.__endTime   = None
        self.__durationPre    = None
        self.__durationBackup = None
        self.__durationPost   = None

    def getName(self):
        '''Get Macrium Reflect task name for this backup'''
        return self.__backupTaskName
        
    def success(self):
        '''Returns true if backup succeeded. If didn't succeed 
        or not started yet, returns false.'''
        return self.__exitCode == 0
        
    def getStartEndTimes(self):
        '''Return a pair of datetime objects'''
        return (self.__startTime, self.__endTime)
        
    def getDurations(self):
        return (self.__durationPre, self.__durationBackup, self.__durationPost)
        
    def registerPrePostTask(self, task):
        '''Register the task for execution. Its executePre() will be called 
        before the backup, and executePost() after the backup. The tasks are 
        executed in order registered for the Pre stage, but in reverse order 
        for the Post stage. '''
        self.__prePostTasks.append(task)
        
    def registerPostTask(self, task):
        '''Convenience method for registering a task for execution when 
        there is not Pre stage to it. It will be executed after all the 
        other tasks that have been registered (via either of the registration 
        methods). Same effect can be achieved by using registerPrePostTask
        but changing the order in which the registrations are done. 
        
        Example: register prepost 1, 2, 3, and post 4, 5; then the order of
        execution will be pre 1, 2, 3; backup; post 3, 2, 1, 4, 5.  This is the 
        same as if registering 5, 4, 1, 2, 3 because the Pre's of 5 and 4 are
        empty.
        
        It is recommended not to call registerPrePostTask as this will
        obfuscate the ordering of calls (though nothing breaks, just hard 
        to read). '''
        self.__prePostTasks.insert(0, task)
        
    def execute(self):
        '''Execute the task, ie the pre task, start backup, monitor its 
        progress, run post task, and print result. '''
        self.__startTime = datetime.now()
        sep = 78 * "="
        print sep
        self.__runPreTasks()
        self.__durationPre = datetime.now() - self.__startTime
        refTime = datetime.now()
        
        try:
            print sep
            self.__start()
            self.__monitor()
            
        finally:
            print sep
            self.__durationBackup = datetime.now() - refTime
            refTime = datetime.now()
            self.__runPostTasks()
            self.__durationPost = datetime.now() - refTime
            self.__endTime = datetime.now()
            
        print sep
    
    def isCompleted(self):
        return self.__exitCode == 0
        
    def printExitCodeStr(self):
        '''Print (to stdout) text string corresponding to Macrium Reflect 
        program exit code.'''
        codeNum = self.__job.returncode
        retCodeMap = ['ok', 'backup error', 'validation error', 'busy']
        try:
            retMsg = retCodeMap[codeNum]
        except IndexError:
            retMsg = 'unknown'

        print 'MRBackupTask: completed with code %s: %s' % (codeNum, retMsg)
        
    def __runPreTasks(self):
        '''Execute the pre method of all prePost tasks, in the order 
        registered. If any of them raises an exception, the run must
        be cancelled, so the post method of all prePost tasks 
        successfully executed so far will be called. '''
        if self.__prePostTasks:
            print 'MRBackupTask: Running PRE tasks'
        else:
            print 'MRBackupTask: No PRE tasks to run'
            return
            
        tmp = []
        for task in self.__prePostTasks:
            try: 
                task.executePre(self)
                tmp.insert(0, task) # successful, save in reverse order
            except Exception:
                print 'MRBackupTask: pre tasking INTERRUPTED! Executing required post tasks and exiting without backup done'
                for task in tmp: 
                    task.executePost(self)
                raise
                
        # list inverted:
        print 'MRBackupTask: All PRE tasks completed'
        self.__prePostTasks = tmp

    def __start(self):
        '''Starts Macrium Reflect backup task named at construction time, 
        and returns immediately. Will raise a FatalError if process could
        not be started (or exited with error). Use __monitor() to wait for
        it to finish. 
        
        TODO: find a way to capture the stdout/err of 
        Reflect; Reflect does something non-standard that bypasses the 
        usual capture techniques.'''
        print 'MRBackupTask: Executing "%s"' % ' '.join(self.__backupCmd)

        try:
            self.__job, self.__stdout = exeProc(self.__backupCmd) #, "reflect")
        except OSError, msg: 
            print 'MRBackupTask: Error executing Macrium Reflect:', msg
            self.__stdout.close()
            raise FatalError(ExitCodes.EXEC_MR)

    def __monitor(self):
        '''Poll the task until it has completed, then return. The exit 
        code of the associated process (Macrium Reflect) is saved in 
        self.__exitCode.'''
        while self.__job.poll() is None:
            time.sleep(1)
            sys.stdout.write('.')
        print '\n'
        self.__exitCode = self.__job.returncode
        if self.__stdout is not None:
            self.__stdout.close()
        print 'Backup task completed'

    def __runPostTasks(self):
        '''Execute the post method of all prePost tasks, in the 
        reverse order registered. '''
        if self.__prePostTasks:
            print 'MRBackupTask: Running post tasks'
        else:
            print 'MRBackupTask: No POST tasks to run'
            return

        for task in self.__prePostTasks:
            task.executePost(self)
        print 'MRBackupTask: All POST tasks completed'
        

class MRBackupPrePostTask:
    '''
    Derive from this class and override one or both of the methods
    then give an instance to MRBackupTask.registerPrePostTask() method.
    The MRBackupTask.execute() will call self.executePre(MRBackupTask)
    before the backup task is executed, and self.executePost(MRBackupTask)
    after. Use self.log(message) to print messages (instead of using 
    'print'). 
    
    Note that the MRBackupTask class assumes that if the pre task has 
    completed successfully, then the post task will be executed even 
    if the backup task has failed. Also, the MRBackupTask runs the post
    backup tasks in reverse order from pre backup tasks. 
    '''
    
    def executePre(self, backupTask):
        '''If your pre-post task doesn't need to do anything at the PRE stage, 
        don't override this method; then just prints a message.'''
        self.log('Nothing to do in pre-task' )
        
    def executePost(self, backupTask):
        '''If your pre-post task doesn't need to do anything at the POST stage, 
        don't override this method; then just prints a message.'''
        self.log('Nothing to do in post-task')
        
    def log(self, *args):
        '''Use this as an easy prefix when printing out messages from subclass,
        as in: "self.log('some message'" which will print 
        'ClassName: some message'.'''
        print '  %-20s:  %s' % (self.__class__.__name__, ' '.join(args))
        

class CaptureScriptStdout(MRBackupPrePostTask):
    '''
    This is a pre/post task to capture the stdout/err of the script 
    using this module. Register an instance with the MRBackupTask as the 
    first registration. Then all print statements will be captured 
    to a file named self.getFilename(). 
    '''
    
    def executePre(self, backupTask):
        logfile = stdouts.getLogFilename('pyscript')
        ff = file(logfile, 'w')
        stdouts.add(logfile)
        sys.stdout = ff
        self.log('Capturing stdout/err to', ff.name)
        
    def executePost(self, backupTask):
        self.log('Restoring stdout to original')
        ff = sys.stdout
        sys.stdout = sys.__stdout__
        ff.close()

class ManageVirtualBoxes(MRBackupPrePostTask):
    '''
    Override the preTask() and postTask() to stop all running 
    VirtualBox virtual machines and restart them after the backup 
    task has completed. 
    
    Note that if a VM failed to be stopped for whatever reason, it 
    will not be resumed after the backup (how could it, its state 
    is then unknown). 
    
    You may change VBOXMANAGE_EXE to point to the VBoxManage.exe 
    on your system if the default is inadequate. This must be done 
    before the call to executePre(), which gets called by 
    MRBackupTask.execute(). 
    '''

    VBOXMANAGE_EXE = r"C:\Program Files\Sun\xVM VirtualBox\VBoxManage.exe"
    
    def __init__(self):
        self.__virtualMachines = []
        
    def executePre(self, backupTask):
        self.__stopAllVirtualMachines()
        self.log('Pre-task completed')
        
    def executePost(self, backupTask):
        self.__resumeAllVirtualMachines()
        self.log('Post-task completed')
        
    def __getVMNameVBMOutput(self, line):
        lineItems = line.split('"')
        #self.log( "line items", lineItems )
        try: 
            vmName = lineItems[1] # format is '"vmName" blabla'
        except IndexError:
            vmName = None
        return vmName
    
    def __stopAllVirtualMachines(self):
        findVMCmd = [self.VBOXMANAGE_EXE, "-q", "list", "runningvms"]
        try:
            out, err = Popen(findVMCmd, stdout=PIPE, stderr=STDOUT).communicate()
        except OSError:
            self.log('VirtualBox (%s) not found on this host, skipping this step' 
                % self.VBOXMANAGE_EXE)
            return
            
        for line in out.split('\n'):
            vmName = self.__getVMNameVBMOutput(line)
            if (not vmName): # or (vmName == "Project Server"):
                continue
                
            exitCode = self.__stopVM(vmName)
            if exitCode == 0:
                self.__virtualMachines.append(vmName)
            else:
                self.log( "Error stopping '%s', can't continue" % vmName )
                raise FatalError(ExitCodes.VM_STOP_FAILED)
                
        if self.__virtualMachines:
            vmList = ','.join(self.__virtualMachines)
            self.log('Saved state of following VM\'s, will resume once backup completed:', vmList)
        else:
            self.log('No Virtual Machines found')
    
    def __stopVM(self, vmName):
        self.log('Stopping Virtual Machine "%s"' % vmName)
        preCmd = [self.VBOXMANAGE_EXE, '-q', 'controlvm', vmName, "savestate"]
        preJob, stdout = exeProc(preCmd, "stopvm")
        exitCode = preJob.wait()
        stdout.close()
        if exitCode != 0:
            self.log('Virtual Machine "%s" could not be stopped!' % vmName)
        return exitCode
        
    def __resumeAllVirtualMachines(self):
        for vmName in self.__virtualMachines:
            self.__startVM(vmName)
        
    def __startVM(self, vmName):
        self.log('Starting VM "%s"' % vmName)
        postCmd = [self.VBOXMANAGE_EXE, '-q', 'startvm', vmName]
        postJob, stdout = exeProc(postCmd, "restartvm")
        exitCode = postJob.wait()
        stdout.close()
        if exitCode != 0:
            self.log('Virtual Machine "%s" could not be resumed!' % vmName)
        

class Main:
    
    def __init__(self):
        backupName = self.__getMRTaskName()
        self.__task = MRBackupTask(backupName)
        
    def registerPrePostTask(self, task):
        self.__task.registerPrePostTask(task)
        
    def registerPostTask(self, task):
        self.__task.registerPostTask(task)
        
    registerPrePostTask.__doc__ = MRBackupTask.registerPrePostTask.__doc__
    registerPostTask.__doc__ = MRBackupTask.registerPostTask.__doc__

    def __runBackup(self):
        self.__task.execute()
        self.__task.printExitCodeStr()
        return self.__task.isCompleted()
    
    def __getMRTaskName(self):
        try:
            backupName = sys.argv[1]
        except IndexError, msg:
            print 'Main: Need the backup task name as first argument'
            raise FatalError(ExitCodes.MISSING_SCRIPT_ARG)

        return backupName

    def __getDestFolder(self):
        try:
            destFolder = sys.argv[2]
        except IndexError, msg:
            return None

        return destFolder

    def __logScriptRun(self):
        startTime, endTime = self.__task.getStartEndTimes()
        success = self.__task.success()
        backupName = self.__task.getName()
        logFile = "pyscripts-%s.log" % date.today()
        print "Main: Logging backup task '%s' to log file '%s'" % (backupName, logFile)
        print "   started %s, ended %s" % (startTime, endTime)
        
        ff = file(logFile, 'a')
        try:
            ff.write( "%s\t%s\t%s\t%s" % (backupName, startTime, endTime, success))
            ff.write('\n')
        finally:
            ff.close()
        
    def __call__(self):
        try:
            self.__runBackup()
            self.__logScriptRun()    
        
        except FatalError, exc:
            print 'Main: ', exc
            sys.exit(exc.exitCode)

        except Exception, exc:
            import traceback
            traceback.print_exc()
            print 'Main:', exc
            sys.exit(ExitCodes.UNKNOWN_CAUSE)

