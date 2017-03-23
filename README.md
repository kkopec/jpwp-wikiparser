# jpwp-wikiparser
[AGH] JPWP (High-level Programming Languages) course project

## Project description

The goal of this project is to write a network application in Python. Created application has to download content of the web page. For simplicity, let's assume that it will be english wikipedia (http://en.wikipedia.org/). Request should contain name of the country, which information about should be downloaded.
After that, information received in response should be stored in database - MongoDB. In case of multiple identical requests, data should be fetched from the database (not downloaded again). Requests should be sent using HTTP methods. Additionally an application should allow for country's search based on a given flag image (flag image should be downloaded from the internet).

All requests should be created in JSON format, with the following schema:

```python
data = {address: address,           # address to send response to, i.e. localhost
        port: port,                 # port for response, i.e. 9091
        type: type,                 # type of request; 'text' or 'image'
        content: request_content    # request content
}
```
Examples of possible requests:
```python
country(Poland)             # returns complete text description of the country - Poland
                            # (omits non-text elements and HTML markup)

country(Poland);tag(Sea)    # analogous to former, but only phrases containing 
                            # word 'Sea' should be returned as a list of elements

country(Poland);getflag     # returns address, under which the country's flag is available

checkflag(http://test.com.flag.gif)     # returns name of the country, which flag of
                                        # was sent as a request parameter
```

## Created application

#### Requirements:
* bs4
* cv2
* pymongo
* requests
* tornado

#### Usage:
```
python server.py
python client.py
```

`db_feeder.py` is a population script for the database. Calculates flags histograms and stores them in the db. Should NOT be used unless it's necessary!
