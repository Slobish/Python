import webbrowser, datetime, time, sys

hours = 0
minutes = 0
seconds = 0
total_break = 0
current_break = 0

def alarm():
    webbrowser.open("https://www.youtube.com/watch?v=xFutjZEBTXs")

def get_time():
    current = datetime.datetime.now()
    values = [current.hour,
              current.minute,
              current.second
              ]
    return values

def config_msg( text ):
    print("[ CONFIGURATION ] {}".format( text ))
    
def error_msg( text ):
    print("[ ERROR ] {}.\nThe program will close in 5 seconds...".format( text ))
    time.sleep(5)
    sys.exit()

def msg( current_break, total_breaks, current):
    print("Taking break number {} out of {} breaks. {}:{}:{}".format(current_break + 1, total_breaks, current[0], current[1], current[2] ))

def compare_time( current, start):
    global seconds, minutes, hours
    current_total = current[0] * 3600 + current[1] * 60 + current[2]
    start_total = start[0] * 3600 + start[1] * 60 + start[2]
    time_dif = current_total - start_total
    config_total = hours * 3600 + minutes * 60 + seconds
    if time_dif >= config_total:
        return True
    return False

def config_time():
    global seconds, minutes, hours
    global total_break
    config_msg("How many breaks?")
    try:
        total_break = int( input("[ CONFIGURATION ] Total breaks: ") )
    except:
        return False
    config_msg("How many hours?")
    try:
        hours = int( input("[ CONFIGURATION ] Hours of work: ") )
    except:
        return False
    config_msg("How many minutes?")
    try:
        minutes = int( input("[ CONFIGURATION ] Minutes of work: ") )
    except:
        return False
    config_msg("How many seconds?")
    try:
        seconds = int( input("[ CONFIGURATION ] Seconds of work: ") )
    except:
        return False
    return True

if not config_time():
    error_msg( "Wrong configuration" )
else:
    config_msg("Configuration OK")

start_time = get_time()

print( "The program is about to start.\n" )

while current_break < total_break:
    """ Waits the time configured and shows an alarm as many times as configured """
    
    current = get_time()
    if compare_time( current, start_time ):
        msg( current_break, total_break, current)
        alarm()
        start_time = get_time()
        current_break += 1
