import os
import tkinter as tk
from tkinter.filedialog import asksaveasfile
import webbrowser
import pandas as pd
import pandas_gbq
import logging
from pandastable import Table
from google.oauth2 import service_account
from dotenv import load_dotenv

# take environment variables from .env file
load_dotenv()

# get variable for service account
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

tableID = 'bigquery-public-data.samples.gsod'

# credentials from a file in .json format necessary for connecting to a bigquery database
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE
)

# create global variable to track how many times 'Generate table' button was clicked
generateTableBtnClickCount = 0

# GUI
class TkinterGUI:
  def createForm(self, parent=None, fields=[]):
    """Create data form with text inputs from passed entry fields
    Args:
      parent: parent element
      fields (array): array of fields that will be used to create the form
    Returns:
      entries
    """
    entries = {}

    for field in fields:
      frame = tk.Frame(parent)
      label = tk.Label(frame, width=15, text=field + ": ", anchor='w', font=('Montserrat', 12), wraplength=120)
      entry = tk.Entry(frame)

      # Add validation to only accept numeric values
      entry.configure(
        validate="key",
        validatecommand=(
          parent.register(self.validate),
          "%P",
        ),
      )
      entry.insert(0, "")

      frame.pack(
        side=tk.TOP,
        fill=tk.X,
        padx=5,
        pady=5
      )
      label.pack(side=tk.LEFT)
      entry.pack(
        side=tk.LEFT,
        expand=tk.YES,
        fill=tk.X
      )
      entries[field] = entry
    return entries

  def validate(self, val):
    """Validate data form entries to allow numbers only
    Args:
      val (int): the value the text would have after the change.
    Returns:
      bool: True if the input is digit-only or empty, and False otherwise.
    """
    return val.isdigit() or val == ""

  def fetchDatabase(self, entries):
    """Fetch data from BigQuery GSOD database with pandas_gbq
    Args:
      entries: entries from data form used to fetch data from GSOD database
    Returns:
      dataframe
    """

    startYear = entries['Start year'].get()
    endYear = entries['End year'].get()
    limit = entries['Max result limit'].get()

    if limit == '':
      limit = 100
    elif int(limit) > 1000:
      tk.messagebox.showerror('Limit Error', 'Maximum results limit has to be lower than 1000')
      return

    query = f"""
      SELECT *
      FROM {tableID}
      {f'WHERE year>{startYear} AND year<{endYear}' if (startYear and endYear) else ''}
      {f'WHERE year>{startYear}' if (startYear and endYear == '') else ''}
      {f'WHERE year<{startYear}' if (startYear == '' and endYear) else ''}
      LIMIT {limit}
    """

    configuration = {
      'query': {
        "useQueryCache": True,
      }
    }

    df = pandas_gbq.read_gbq(
      query,
      credentials=credentials,
      configuration=configuration,
    )

    # Add logger to log progress of longer queries
    logger = logging.getLogger('pandas_gbq')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    return df

  def displayTable(self, parent=None, entries=[]):
    """Generate table from entries to display in tkinter window, with possibility of plotting (chart creation)
    Args:
      parent: parent of table to display
      entries: entries from data form used to fetch data from GSOD database
    """
    global generateTableBtnClickCount
    generateTableBtnClickCount += 1

    query_job = self.fetchDatabase(entries)

    # if table was created before - delete it, so it would not overwrite a new one
    if generateTableBtnClickCount != 1:
      for w in parent.winfo_children():
        w.destroy()

    df = pd.DataFrame(query_job)
    pt = Table(parent, dataframe=df, height=250, showstatusbar=True, showtoolbar=True)
    pt.model.df = df
    pt.show()

    # in order for the data to be displayed immediately, not only after user interacts with the table - redraw it
    pt.redraw()

    return

  def generateReport(self, entries):
    """Generate report in CSV format from database
    Args:
      entries: entries from data form used to fetch data from GSOD database
    Returns:
      file: in csv format if successful, otherwise ends function
    """

    startYear = entries['Start year'].get()
    endYear = entries['End year'].get()
    limit = entries['Max result limit'].get()

    if limit == '':
      limit = 100
    elif int(limit) > 1000:
      tk.messagebox.showerror('Max Limit Exceeded', 'Maximum results limit has to be lower than 1000')
      return

    # File name config
    startYearName = f'from={startYear}' if startYear != '' else ''
    endYearName = f'to={endYear}' if endYear != '' else ''
    fileName = f'gsod_{startYearName}{endYearName}limit={limit}'

    # Ask user where they want to save a generated report in csv format
    files = [('CSV Files', '*.csv')]
    file = asksaveasfile(filetypes=files, defaultextension=files, initialfile=fileName)
    df = self.fetchDatabase(entries)

    if file and (file is not None):
      csv = df.to_csv(file.name, index=False)
      return csv
    else:
      return

  def fetchEntries(entries):
    """Fetch entries from data form
    Args:
      entries: entries from data form
    """

    for entry in entries:
      field = entry[0]
      text = entry[1].get()

  def checkIfBtnWasClicked(self, btn):
    btn += btn

  def centerGUI(self, parent, width, height):
    """Center root window on user's screen
    Args:
      parent: parent of window
      width: width of window
      height: height of window
    """

    # get screen width and height
    ws = parent.winfo_screenwidth()  # width of the screen
    hs = parent.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (width / 2)
    y = (hs / 2) - (height / 2)
    parent.geometry('%dx%d+%d+%d' % (width, height, x, y))

  def __init__(self, root=None, fields=None):
    """Center root window on user's screen
    Args:
      root: root of the object
      fields: fields used for creation of entries in data form
    """

    root.title('Report generator')

    vertScrollbar = tk.Scrollbar(root, orient="vertical")
    vertScrollbar.pack(side="right", fill="y")
    w = 850  # width for the Tk root
    h = 650  # height for the Tk root
    self.centerGUI(root, w, h)  # center tkinter window on screen

    def openUrl(url):
      """Opens given url in browser
      Args:
        url (string): url to open
      """

      webbrowser.open_new(url)
      return

    # DB information text
    link = "https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=samples&t=gsod&page=table&_ga=2" \
           ".126965706.635408540.1684247329-620543960.1665516938"
    self.dbInfo = tk.Text(root, height=8, font=('Lato', 12), wrap=tk.WORD)
    self.dbInfo.pack(padx=10, pady=15, fill=tk.BOTH)
    self.dbInfo.tag_configure("dbInfo", justify='center', spacing1=5, spacing2=1.5, spacing3=5)
    self.dbInfo.insert(tk.END, "(Please scroll to read the whole text) \n This app allows you to generate and "
                               "download data from ")
    self.dbInfo.insert(tk.END, "GSOD BigQuery", ('link', link))
    self.dbInfo.insert(tk.END,
                       " public database in a .csv format. \n GSOD database contains weather information collected by "
                       "NOAA, such as precipitation amounts and wind speeds from late 1929 to early 2010. \n You may "
                       "specify the start and end year of the data you would like to download. The default limit of "
                       "downloaded results is 100, for not overloading the query the maximum limit is set to 1000.\n"
                       "The entries below are validated and accept numbers only. \n In order to create chart from a "
                       "generated table select rows/columns you'd like to plot and click on the the 'Plot selected' "
                       "button in the toolbar on the table's right. The plot viewer will open in a new window.")
    self.dbInfo.tag_add("dbInfo", "1.0", "end")
    self.dbInfo.config(
      state=tk.DISABLED)  # disable state MUST be AFTER text insert, otherwise the text won't be visible
    self.dbInfo.tag_configure('link', foreground="blue")
    self.dbInfo.tag_bind('link', '<Double-Button-1>', lambda e, url=link: openUrl(url))

    #  Generate data form
    self.fields = ['Start year', 'End year', 'Max result limit']
    ents = self.createForm(root, fields)

    # Action buttons
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP)
    self.btnReport = tk.Button(frame, text='Download CSV table report', command=(lambda: self.generateReport(ents)))
    self.btnReport.pack(side=tk.LEFT, padx=5, pady=5)

    self.btnTable = tk.Button(frame, text='Generate table', command=(lambda: self.displayTable(tableFrame, ents)))
    self.btnTable.pack(side=tk.LEFT, padx=5, pady=5)

    # create frame for table generated after btnTable is clicked
    tableFrame = tk.Frame(root)
    tableFrame.pack(
      side=tk.BOTTOM,
      fill=tk.BOTH,
      expand=True,
      padx=5,
      pady=5
    )


if __name__ == '__main__':
  root = tk.Tk()
  fields = ['Start year', 'End year', 'Max result limit']
  gui = TkinterGUI(root, fields)

  root.mainloop()
