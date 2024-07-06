# COMMANDS MESSAGES
START_MESSAGE = "Hello, <b>{}</b>! Looks like we have another gym goer right here!\n\n"+\
                "Reminder\n" +\
                "• You must book the gym with a buddy for safety\n" +\
                "• Each resident can book up to 4 slots per week\n" +\
                "• Each slot will be minimum 1h and maximum 1.5h\n\n" +\
                "/help - for all commands\n" +\
                "/register - register your email before booking\n" +\
                "/verify - verify email for authentication\n\n" +\
                "/book - book your gym slot now!\n"

HELP_MESSAGE = "What can this bot do?\n\n" +\
                "/register - register your email before booking\n" +\
                "/verify - verify email for authentication\n\n" +\
                "/book - book your gym slot now!\n" +\
               "/cancel - cancel slots to free them up for others :)\n\n" +\
               "/schedule - view available time slots here\n\n" +\
               "/exco - contact the exco on any queries, feedback and damages\n"
               #"/delete - delete your account and data\n\n" +\
               #"/history - view your slots for the week\n\n" +\

EXCO_MESSAGE = "Contact us! we are happy to help!\n" +\
               "Benjamin - @benjaminseowww\n" +\
               "Hamzi - @zzimha\n"
                #"Jedi - @JediKoh\n" +\
               #"Justin - @jooostwtk"

CANCEL_NOSLOTS_MESSAGE = "You do not have any upcoming slots!"

SCHEDULE_MESSAGE = "Here are the available slots for the week:\n" +\
                   "https://docs.google.com/spreadsheets/d/1r1r0I0HvKDivze8YMj9BNZfs4p8Z957XWc498QUaSU0/edit?usp=sharing"
                   
NOT_REGISTERED_MESSAGE = "You are not registered yet! Please register using /register and verify using /verify before booking"

NOT_VERIFIED_MESSAGE = "You are not verified yet! Please verify your email using /verify before booking"

# FORM 
FORM_DECLARATION = "• I understand it is my personal responsibility to be in good physical health to carry out the sessions " +\
                   "in the gym and bring personal medication if needed\n\n" +\
                   "• I understand that all users must clean all equipment used before and after use.\n\n" +\
                   "• I have read and declared all the above to be true.\n"


BOOKING_USER_DETAILS_STRING = "Name: {}\n" +\
                              "Telegram Handle: @{}\n" +\
                              "Room Number: #{}\n\n" +\
                              "Buddy Name: {}\n" +\
                              "Buddy Telegram Handle: @{}\n" +\
                              "Buddy Room Number: #{}"
BOOKING_DATETIME_STRING = "Date: {}\nTime: {} - {}"

# CANCEL
DEFAULT_CANCEL_REMARK = "Wrong Booking Timing"

# OTP EMAIL
OTP_EMAIL_MESSAGE = "Subject: OTP for RC4Lifting Official Gym Booking Telegram Bot\n\n" +\
                    "Hello! Your OTP for the RC4Lifting Official Gym Booking Telegram Bot is: {}\n" +\
                    "If you did not request this OTP, please notify the exco immediately, we will investigate this case of misued email"