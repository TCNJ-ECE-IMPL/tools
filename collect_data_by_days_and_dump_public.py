# Semi automatic scraping - user:
#   selects dates
#   sets Sense user name
#   sets Sense password
#   sets debug_flag (indicates whether to save debug information)

import re
import datetime as dt
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

############################################# User settings ###################################
start_date      = dt.date(2020, 12, 14)
end_date        = dt.date(2020, 12, 29)
sense_username  = "insert_your_email_address@domain.com"
sense_password  = "pUt_YOUr_passW0rd_h3r3"
debug_flag      = 1                 # set to 0 to avoid saving lots of extra files
###############################################################################################

one_day_idx     = 1156                  # seems like 1156 samples per day
vertical_offset = 85                    # compensate for the plot's incorrect tick lines!
# Open file for saving all data
fd_full = open( "all_data.csv", "w" )

# Convert dates to ordinals
start_date  = start_date.toordinal()
end_date    = end_date.toordinal()

# Start up Selenium Server, and wait a bit
remDr = webdriver.Firefox()
time.sleep(3)

# Convert dates fromordinals
this_date = dt.date.fromordinal(start_date)
next_date = dt.date.fromordinal(start_date + 1)

# Navigate to the web page
the_url = "https://home-beta.sense.com/meter?start=%s&end=%s" % (str(this_date), str(next_date))
if debug_flag:
    print(the_url)
remDr.get(the_url)

# Wait for a response
time.sleep(5)
    
# The first time through will ask for user name and pssword
webElem = remDr.find_element_by_xpath('//*[@id="application__main"]/div/div[1]/form/div[1]/input')
webElem.send_keys(sense_username)
time.sleep(2)
webElem = remDr.find_element_by_xpath('//*[@id="application__main"]/div/div[1]/form/div[2]/input')
webElem.send_keys(sense_password)
webElem.send_keys(Keys.RETURN)

# Wait for page to load
time.sleep(10)

# Find and save the y ccoordinate for the x-axis as the zero for future relative measurements
# Values change with different browser window sizings
webElem = remDr.find_element(By.CLASS_NAME, 'pm__x-axis')
outer = webElem.get_attribute('outerHTML')
outer = re.sub('.*0, ', "", outer)
outer = re.sub('\).*$', "", outer)
zero_mark = int(float(outer)+0.5)

for date_idx in range (start_date, end_date + 1):
    # Pull out the max for the waveform for calibration
    webElem = remDr.find_element(By.CLASS_NAME, 'pm__max-label')
    outer = webElem.get_attribute('outerHTML')
    outer = re.sub('<text class=\"pm__max-label\" x=\"16\" y=\"32\">', '', outer)
    outer = re.sub('w</text>', '', outer)
    max_mark = int(float(outer)+0.5)
    
    # Find and save the y ccoordinate for the x-axis as the zero for future relative measurements
    # Values change with different browser window sizings
    webElem = remDr.find_element(By.CLASS_NAME, 'pm__view')
    outer = webElem.get_attribute('outerHTML')
    
    m = re.search( 'height="([0-9\.]+)"', outer )
    if (m):
        ylim = int(float(m.group(1))+0.5)
        if debug_flag:
            print( "ylim = %d" % ylim )
    else:
        print("Couldn't find height field!")
        exit();
            
    if debug_flag:
        txt_file = "sense_data_%s.txt" % str(this_date)
        csv_file = "sense_data_%s.csv" % str(this_date)
    
        fd_txt = open(txt_file, "w")
        fd_txt.write( outer )
        fd_txt.close()
        
        fd_txt = open(txt_file, "r")
        outer = fd_txt.read()
        fd_txt.close()

        fd_csv = open(csv_file, "w")
    
    # Note: *? is the non-greedy match
    pattern = r'd="M(.*)pm__gradient'
    m = re.search( pattern, outer )
    if m:
        outer = m.group(1)
    
    # Note: *? is the non-greedy match
    pattern = r'L(.*?)[HL]'
    matching = re.findall(pattern, outer)

    for match in matching:
        m=re.search( "^(.*),(.*)$", match )
        
        if (m):
            x = int(m.group(1))
            y = int(m.group(2))
            # For some reason Sense returns -one_day_idx .. 2*one_day_idx.  Select out center cut!
            if ( x >= 0 and x < one_day_idx ):
                if debug_flag:
                    fd_csv.write( "%d , %f\n" % (x, float(ylim-y)/(ylim-vertical_offset)*max_mark) )
                fd_full.write( "%d , %f\n" % (x, float(ylim-y)/(ylim-vertical_offset)*max_mark) )
    
    if debug_flag:
        fd_csv.close()
    
    if date_idx < end_date:
        # Navigate to the next web page
        this_date = dt.date.fromordinal(date_idx + 1)
        next_date = dt.date.fromordinal(date_idx + 2)
        the_url = "https://home-beta.sense.com/meter?start=%s&end=%s" % (str(this_date), str(next_date))
        if debug_flag:
            print(the_url)
        remDr.get(the_url)
        
        # Wait for page to load
        time.sleep(10)

fd_full.close()
