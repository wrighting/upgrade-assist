
class Report(object):

    def actionRequired(self, message, customFile, oldFile, newFile):
        print()
        print("You need to check: " + customFile)
        print(message)
        print("Old file:" + oldFile)
        print("New file:" + newFile)
        print()

    def info(self, message):
        print (message)
        pass

    def warning(self, message):
    #    print message
        pass

    def error(self, message):
        print(message)
        pass
