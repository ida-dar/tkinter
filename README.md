### Tkinter
This app allows you to generate and download data from [GSOD BigQuery](https://cloud.google.com/bigquery/public-data#sample_tables) public database in a .csv format build with Tkinter. GSOD database contains weather information collected by NOAA, such as precipitation amounts and wind speeds from late 1929 to early 2010.

In the app you may specify the start and end year, and the maximum result size of the data you would like to download. The default limit of downloaded results is 100, for not overloading the query the maximum limit is set to 1000.

All entries (start and end year, and max result limit) are validated and accept numbers only.

In order to create chart from a generated table select rows/columns you'd like to plot and click on the 'Plot selected' button in the toolbar on the table's right. The plot viewer will open in a new window.

I plan on developing the app in the future to support more databases and more query parameters.

### Requirements
All requirements are listed in the requirements.txt file. However, I decided to list some of the necessary ones too.

* python==3.11
* tkinter==8.6
* google-auth==2.19.1
* google-auth-oauthlib==1.0.0
* google-cloud-bigquery==3.11.0
* google-cloud-bigquery-storage==2.20.0
* google-cloud-core==2.3.2
* pandas==2.0.2
* pandas-gbq==0.19.2
* pandastable==0.13.1
* tqdm==4.65.0

### Get started
To run the app you need a service account credentials necessary for connecting with a database. If you have them:
* replace `SERVICE_ACCOUNT_FILE` below with the path to your service account file:
```
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE
)
```

OR

* create an .env file and create a `SERVICE_ACCOUNT_FILE` variable like this `SERVICE_ACCOUNT_FILE='/Path/to/service_account.json'`


In the terminal:
* install all dependencies
* run `python main.py`
* to quit: ctrl-c