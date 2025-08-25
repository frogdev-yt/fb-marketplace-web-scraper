Very hard coded basic but functional web scraper I made to help my friend look for deals on motorcycles
Some gross specific hard coded aspects to get around marketplace bot detection / temporary html tags

Currently programmed to have future support for custom search options and prerequisites (only for vehicles at the moment, but can be easily changed)

Next version (if updated) will feature:
- UI to add specific general purpose search options with price prereqs
- toggling of email notifications
- Changing of search length, scroll speed, search repeat cooldown, with default values to match current values if user does not wish to mess with these  



TO USE:

- First, run the initialize file to log into your facebook account, generate required web driver user data and set email for notifications when listings are found.
- Then just run the project file and leave it running, it will continue to cycle through chosen search terms until reaching the end of all provided, then will wait for a fixed cooldown period and repeat
