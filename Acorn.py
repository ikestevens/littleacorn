from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class Acorn():
    '''
    Acorn Class for scanning Goodreads to-reads and finding available Audiobooks from Arlington Library
    '''
    def __init__(self, library_card, gr_username=None):

        self.DRIVER_PATH = '/Users/isaacstevens/Downloads/chromedriver 2'
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--incognito")
        self.library_card = library_card
        if 'goodreads.com' in gr_username:
            self.listname = gr_username
            self.gr_book_df = None
        else:
            self.gr_username = gr_username
        self.library_url = "https://arlington.overdrive.com/"

    def get_to_read(self):
        titles = []
        authors = []
        avg_rating = []
        date_added = []
        goodread_url = "https://www.goodreads.com/" + self.gr_username
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)
        wd.get(goodread_url)
        time.sleep(4)
        wd.get(goodread_url) # Load twice to get rid of popup
        time.sleep(10)
        all_links = wd.find_elements_by_xpath("//a[@class='actionLinkLite userShowPageShelfListItem']")
        for link in all_links:
            if 'to-read' in link.text:
                element = link
        element.send_keys("\n")
        try:
            time.sleep(10)
            loaded = wd.find_element_by_xpath("//div[@id='infiniteStatus']")
        except:
            time.sleep(20)
            loaded = wd.find_element_by_xpath("//div[@id='infiniteStatus']")
        while loaded.text.split(' ')[0] != loaded.text.split(' ')[2]:
            wd.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)
            loaded = wd.find_element_by_xpath("//div[@id='infiniteStatus']")
        table =  wd.find_element_by_xpath("//table[@id='books']")
        for row in table.find_elements_by_xpath(".//tr"):
            for td in row.find_elements_by_xpath(".//td[@class='field title']"):
                titles.append(td.text)
            for td in row.find_elements_by_xpath(".//td[@class='field author']"):
                authors.append(td.text)
            for td in row.find_elements_by_xpath(".//td[@class='field avg_rating']"):
                avg_rating.append(td.text)
            for td in row.find_elements_by_xpath(".//td[@class='field date_added']"):
                date_added.append(td.text)

        self.gr_book_df = pd.DataFrame({'Title': titles,'Author': authors,'Avg Rating': avg_rating,'Date Added': date_added})

        wd.close()
        wd.quit()

        return True

    def set_to_read(self, path):
        '''
        Test Function to directly read in Goodreads to-read list"
        '''
        self.gr_book_df = pd.read_csv(path, index_col=0)

        return True

    def find_audiobook(self, Flag = None):
        # add library website
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)
        # load the page
        wd.get(self.library_url)
        time.sleep(5)

        #login
        try:
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        except:
            time.sleep(10)
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        if self.library_card == None:
            cardNum = wd.find_element_by_id("username").send_keys("1401233")
        else:
            cardNum = wd.find_element_by_id("username").send_keys(self.library_card)
        signIn = wd.find_element_by_xpath("//button[@class='signin-button button secondary']")
        signIn.click()
        time.sleep(5)

        if self.library_card == None:
            self.loan_df = pd.DataFrame()
            self.hold_df = pd.DataFrame()
        else:
            #Get Loan List
            loan_url = 'https://arlington.overdrive.com/account/loans'
            wd.get(loan_url)
            loan_books = wd.find_elements_by_xpath("//div[@class='title-contents']")
            loan_list = []
            for loan in loan_books:
                loan_results = loan.text.split("\n")
                loan_list.append((loan_results[1], loan_results[2], loan_results[0]))
            self.loan_df = pd.DataFrame(loan_list, columns = ['Title', 'Author', 'Status'])

            #Get My_Wait_List List
            hold_url = 'https://arlington.overdrive.com/account/holds'
            wd.get(hold_url)
            hold_books = wd.find_elements_by_xpath("//div[@class='title-details-container']")
            hold_list = []
            for hold in hold_books:
                hold_results = hold.text.split("\n")
                time_left = ' '.join([str(v) for v in hold_results[4].split(" ")[2:]])
                hold_list.append((hold_results[0], hold_results[1], hold_results[3], time_left))
            hold_list = sorted(hold_list, key=lambda x: (len(x[3].split())==3, x[3] if len(x[3].split())==2 else int(x[3].split()[1]) ) )
            self.hold_df = pd.DataFrame(hold_list, columns = ['Title', 'Author', 'Position', 'Wait Time Left'])

        avail_list = []
        wait_list = []
        if self.gr_book_df == None:
            for book in self.book_list_list:
                search_bar = wd.find_element_by_id("nav-search-mobile")
                search_bar.clear()
                book_name = ' '.join(book.split(" ")[:5])
                search_bar.send_keys(book_name)
                search_bar.send_keys(Keys.RETURN)
                books = wd.find_elements_by_xpath("//li[@class='js-titleCard Item']")
                audio = "AUDIOBOOK"
                avail = 'AVAILABLE'
                wait = 'WAIT LIST'
                for book in books:
                    if book_name in book.text and audio in book.text and avail in book.text:
                        results = book.text.split("\n")
                        avail_list.append((results[1], results[2].replace("by ", ""), results[0]))
                    if book_name in book.text and audio in book.text and wait in book.text:
                        results = book.text.split("\n")
                        book.click()
                        full_time = wd.find_element_by_xpath("//span[@class='waitingText']").text
                        if 'Available soon' in full_time:
                            wait_time = ' '.join(full_time.split(" ")[-2:])
                        else:
                            wait_time = ' '.join(full_time.split(" ")[-3:])
                        wait_list.append((results[1], results[2].replace("by ", ""), wait_time, results[0]))
                        break

            self.avail_df = pd.DataFrame(avail_list, columns = ['Title', 'Author', 'Status'])
            wait_list = sorted(wait_list, key=lambda x: (len(x[2].split())==3, x[2] if len(x[2].split())==2 else int(x[2].split()[1]) ) )
            self.wait_df = pd.DataFrame(wait_list, columns = ['Title', 'Author', 'Wait Time', 'Status'])

        else:
            for index, row in self.gr_book_df.iterrows():
                search_bar = wd.find_element_by_id("nav-search-mobile")
                search_bar.clear()
                book_name = ' '.join([str(v) for v in row['Title'].split(" ")[:5]])
                search_bar.send_keys(book_name)
                search_bar.send_keys(Keys.RETURN)
                books = wd.find_elements_by_xpath("//li[@class='js-titleCard Item']")
                audio = "AUDIOBOOK"
                avail = 'AVAILABLE'
                wait = 'WAIT LIST'
                for book in books:
                    if book_name in book.text and audio in book.text and avail in book.text:
                        results = book.text.split("\n")
                        avail_list.append((results[1], results[2].replace("by ", ""), results[0]))
                    if book_name in book.text and audio in book.text and wait in book.text:
                        results = book.text.split("\n")
                        book.click()
                        full_time = wd.find_element_by_xpath("//span[@class='waitingText']").text
                        if 'Available soon' in full_time:
                            wait_time = ' '.join(full_time.split(" ")[-2:])
                        else:
                            wait_time = ' '.join(full_time.split(" ")[-3:])
                        wait_list.append((results[1], results[2].replace("by ", ""), wait_time, results[0]))
                        break

            self.avail_df = pd.DataFrame(avail_list, columns = ['Title', 'Author', 'Status'])
            wait_list = sorted(wait_list, key=lambda x: (len(x[2].split())==3, x[2] if len(x[2].split())==2 else int(x[2].split()[1]) ) )
            self.wait_df = pd.DataFrame(wait_list, columns = ['Title', 'Author', 'Wait Time', 'Status'])
        wd.close()
        wd.quit()
        return self.avail_df, self.wait_df, self.loan_df, self.hold_df

    def checkout_books(self, titles):
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)

        # load the page
        wd.get(self.library_url)
        time.sleep(10)

        #login
        try:
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        except:
            time.sleep(10)
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        cardNum = wd.find_element_by_id("username").send_keys(self.library_card)
        signIn = wd.find_element_by_xpath("//button[@class='signin-button button secondary']")
        signIn.click()
        time.sleep(5)

        for title in titles:
            search_bar = wd.find_element_by_id("nav-search-mobile")
            search_bar.clear()
            search_bar.send_keys(title)
            search_bar.send_keys(Keys.RETURN)

            books = wd.find_elements_by_xpath("//li[@class='js-titleCard Item']")
            avail = 'AVAILABLE'
            for book in books:
                if title in book.text and "AUDIOBOOK" in book.text and avail in book.text:
                    book.click()
                    borrow_button = wd.find_element_by_xpath("//button[@data-type-name='Audiobook']")
                    borrow_button.click()
                    time.sleep(2)
                    yes_borrow = wd.find_element_by_xpath("//button[contains(text(), 'Borrow')]")
                    yes_borrow.click()
                    break
        wd.close()
        wd.quit()

    def waitList_books(self, titles):
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)

        # load the page
        wd.get(self.library_url)
        time.sleep(10)

        #login
        try:
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        except:
            time.sleep(10)
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        cardNum = wd.find_element_by_id("username").send_keys(self.library_card)
        signIn = wd.find_element_by_xpath("//button[@class='signin-button button secondary']")
        signIn.click()
        time.sleep(5)

        for title in titles:
            search_bar = wd.find_element_by_id("nav-search-mobile")
            search_bar.clear()
            search_bar.send_keys(title)
            search_bar.send_keys(Keys.RETURN)

            books = wd.find_elements_by_xpath("//li[@class='js-titleCard Item']")
            wait_words = 'WAIT LIST'
            for book in books:
                if title in book.text and "AUDIOBOOK" in book.text and wait_words in book.text:
                    book.click()
                    wait_button = wd.find_element_by_xpath("//button[@data-type-name='Audiobook']")
                    wait_button.click()
                    time.sleep(2)
                    try:
                        exit_button = wd.find_element_by_xpath("//a[@class='close-reveal-modal js-close']")
                        exit_button.click()
                    except:
                        yes_hold = wd.find_element_by_xpath("//button[contains(text(), 'PLACE A HOLD')]")
                        yes_hold.click()
                        exit_button = wd.find_element_by_xpath("//a[@class='close-reveal-modal js-close']")
                        exit_button.click()
                    break

        wd.close()
        wd.quit()

    def returnBooksOnLoan(self, titles):
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)

        # load the page
        wd.get(self.library_url)
        time.sleep(10)

        #login
        try:
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        except:
            time.sleep(10)
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        cardNum = wd.find_element_by_id("username").send_keys(self.library_card)
        signIn = wd.find_element_by_xpath("//button[@class='signin-button button secondary']")
        signIn.click()
        time.sleep(5)

        loan_books = wd.find_elements_by_xpath("//div[@class='title-contents']")
        i=0
        for loan in loan_books:
            for title in titles:
                if title in loan.text:
                    return_button = wd.find_elements_by_xpath("//a[@data-reveal-id='return-modal']")
                    return_button[i].click()
                    yes_return = wd.find_element_by_xpath("//a[@aria-label='Return title']")
                    wd.execute_script("arguments[0].click();", yes_return)
            i+=1
        wd.close()
        wd.quit()

    def releaseBooksOnHold(self, titles):
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)

        # load the page
        wd.get(self.library_url)
        time.sleep(10)

        #login
        try:
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        except:
            time.sleep(10)
            element = wd.find_element_by_link_text("SIGN IN")
            element.click()
        cardNum = wd.find_element_by_id("username").send_keys(self.library_card)
        signIn = wd.find_element_by_xpath("//button[@class='signin-button button secondary']")
        signIn.click()
        time.sleep(5)

        hold_books = wd.find_elements_by_xpath("//div[@class='title-contents']")
        i=0
        for hold in hold_books:
            for title in ["This one not there", "A Short History of Nearly Everything"]:
                if title in loan.text:
                    release_button = wd.find_elements_by_xpath("//button[contains(text(), 'Remove')]")
                    release_button[i].click()
                    yes_release = wd.find_element_by_xpath("//button[contains(text(), 'Remove hold')]")
                    wd.execute_script("arguments[0].click();", yes_release)
            i+=1
        wd.close()
        wd.quit()

    def getListBooks(self):
        list_url = self.listname
        wd = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options = self.chrome_options)
        wd.set_window_size(700, 600)
        wd.get(list_url)
        time.sleep(5)

        flag = True
        self.book_list_list = []
        while flag:
            wd.find_element_by_xpath("//button[@class='gr-iconButton']")
            books = wd.find_elements_by_xpath("//a[@class='bookTitle']")
            for book in books:
                self.book_list_list.append(book.text)
            try:
                next_link = wd.find_element_by_xpath("//a[@rel='next']")
                next_link.click()
                try:
                    exit = wd.find_element_by_xpath("//button[@class='gr-iconButton']")
                    wd.execute_script("arguments[0].click();", exit)
                except:
                    continue
            except:
                flag = False

        print(len(self.book_list_list))

        wd.close()
        wd.quit()

        return self.book_list_list

if __name__ == "__main__":
    #Test to see if it works

    acorn_test = Acorn("1401233", 'ikestevens')
    acorn_test.get_to_read()
    #acorn_test.set_to_read("my_audiobook_list.csv")
    avail_df, wait_df, loan_df, hold_df = acorn_test.find_audiobook()

    avail_df.to_csv('avail_df.csv')
    wait_df.to_csv('wait_df.csv')
    loan_df.to_csv('loan_df.csv')
    hold_df.to_csv('hold_df.csv')
