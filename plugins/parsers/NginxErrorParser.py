__author__ = 'lwz'

from base import LogsterParser, LogsterParsingException


class NginxErrorParser(LogsterParser):

    def __init__(self):
        """
       Initialize any data structures or variables needed for keeping track
       of the tasty bits we find in the log we are parsing.
       """
        self.some_value = 0
        self.reg = None

    def parse_line(self, line):
        """
        This function should digest the contents of one line at a time, updating
       object's state variables. Takes a single argument, the line to be parsed.
        """
        # TODO, FIRST NEED TO RE INIT THE __init__ VALUES, EXCEPT THE REG..

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
            # TODO, save the parsed value ...

            else:
                raise LogsterParsingException, "regmatch failed to match"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e

    def get_state(self, duration):
        """ Run any necessary calculations on the data collected from the logs
        :param duration:
        and return a list of metric objects.
        """


        # Return a list of metrics objects
        return []