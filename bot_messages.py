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
                "/verify - verify email for authentication\n" +\
                "/delete - delete your nus data from our system\n\n" +\
                "/book - book your gym slot now!\n" +\
                "/cancel - cancel slots to free them up for others :)\n\n" +\
                "/schedule - view available time slots here\n\n" +\
                "/exco - contact the exco on any queries, feedback and damages\n"
                

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

# REGISTRATION
PDPA_PRECLAUSE_MESSAGE = "We will be collecting your <b>NUSNET ID</b> and <b>NUS Email</b>\n" +\
                         "Read the PDPA clause below and select 'I consent' to continue"
PDPA_CLAUSE_MESSAGE = "<b>Personal Data Protection Act (PDPA) Clause</b>\n\n" +\
                      "Please take note of the following:\n\n" +\
                      "(i) The data collected in this bot will only be used for RC4 gym bookings\n" +\
                      "(ii) The collected data will only be used for administrative and financial-related purposes by the College and/or University, where required.\n" +\
                      "(iii) The organising committee will retain the collected data only until the end of the AY.\n\n" +\
                      "Should you have any questions regarding this bot, please contact the exco with /exco.\n" +\
                      "Should you have any questions/clarifications, please contact Aditya Jayaraj, General Secretary of the RC4 10th CSC, via email at aditya.j@u.nus.edu.\n\n" +\
                      "Should you have any concerns regarding this, please write to the College Master or either of the contacts provided below:\n" +\
                      "(i) Dr. Naviyn, Director of Student Life, RC4 (Email: rc4npb@nus.edu.sg)\n" +\
                      "(ii) You Cheng, Assistant Senior Manager, RC4 (Email: rc4tyc@nus.edu.sg)"
                      
PDPA_QUESTION_MESSAGE = "I consent to providing my personal data for the aforementioned purpose." +\
                        "I also agree to receive important updates pertaining to matters contained in this survey." +\
                        "All personal information will be kept confidential and used only for the aforementioned purpose." +\
                        "I understand that should I wish to withdraw my consent for the organising committee to contact me for the purposes stated above," +\
                        "I can notify Aditya Jayaraj, Residential College 4, College Students' Committee General Secretary, in writing to aditya.j@u.nus.edu." +\
                        "The organising committee will then remove my personal information from their database," +\
                        "and I allow 7 business days for my withdrawal of consent to take effect."

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
OTP_EMAIL_SUBJECT = "OTP for RC4Lifting Official Gym Booking Telegram Bot"
OTP_EMAIL_MESSAGE = "Hello! \n\nYour OTP for the RC4Lifting Official Gym Booking Telegram Bot is:\n\n" +\
                    "{}\n\n" +\
                    "If you did not request for this OTP, please notify the exco immediately by '/exco' in the telegram bot (https://t.me/rc4lifting_bot)\n"