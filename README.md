# About
```
@article{26583204_325243423_2019, 
    author = {Vladimir Barakhnin and Olga Kozhemyakina and Ravil Mukhamediev and Yulia Borzilova and Kirill Yakunin}, 
    keywords = {natural language processing, streaming word processing, text analysis information systemdevelopment of a text corpus processing system},
    title = {The design of the structure of the software system for processing text document corpus},
    year = {2019},
    number = {4 Vol.13},
    pages = {60-72},
    url = {https://bijournal.hse.ru/en/2019--4 Vol.13/325243423.html},
}
```

Media-monitoring system which solves the following problems:

- Parsing of news web sites using custom configurable Spider (<b>Scrapy</b>) 
- Storage (<b>Redis, PostgreSQL, Elasticsearch</b>)
- NLP data preprocessing (<b>PyMorphy2, NLTK, Gensim</b>) 
- Topic modelling (<b>LDA, BigARTM, ETM</b>), including dynamic models (<b>Custom DTM, DETM</b>)
- Classification of documents according to arbitrary criteria (<b>M4A, traditional ML approach</b>)
- Visualization (<b>Django, HTML+CSS+JS, Plotly, MapBox</b>)
- Automatic report generation (<b>LaTex+Jinja2</b>)

# Architecture

All components of the system are implemented as __Docker__ containers. Such implementation allows components and subsystems to work independently, interchangeable and allows easy scalability.
<div align="center">
    <img src="https://i.ibb.co/SNpjH1Y/Picture1.png"/>
    <p>Architecture</p>
</div>

<b>Airflow</b> is an <b>ETL</b> subsystem, upon which scrapping spiders Spider(<b>Scrapy</b>) which are being stored in <b>PostgreSQL</b> as a persistent structured SQL storage. Data obtained through preprocessing, modifications and modelling is stored in <b>ElasticSearch</b>, which is the main storage for pre-calculated results necessary for displaying dashboard and reports.

# Interface

Topic Document Dynamics             |  Criteria Dynamics
:-------------------------:|:-------------------------:
![analytics1](https://i.ibb.co/4SnGh8g/rsz-1analytics-1.png)  |  ![analytics2](https://i.ibb.co/gjzbjZQ/rsz-analytics-2.png)

The system also provides tools for visualization, such as dynamics of publications of topics in media according to various criteria, histograms of criteria value distribution, distributions amongh sources, etc.
<div align="center">
    <img src=https://i.ibb.co/JzKvnvJ/rsz-dtm.jpg" >
    <p>Dynamic Topic Modelling</p>
</div>

__*Mapping DTM*__ is a custom algorithm for analyzing topic dynamics based on context semantic mapping (__Context Fuzzy Jaccard__).
It allows to visualize topics lifesycle, analyze changes in vocabulary, classify topics by their dynamic characteristics in order to distinguish events, informational attacks, long-term trends, etc.

<div align="center">
    <img src=https://i.ibb.co/1601df5/68747470733a2f2f692e696d6775722e636f6d2f493149464d35612e6a706722.jpg">
    <p>Analytics Dashboard</p>
</div>
                                             
__Dashboards__ - set of configurable widgets, which are able to perform the above mentioned visualizations.
Dashboard can be configured according to client's needs and does __not require additional development__.
*Monitoring objects* are implemented as a special NER requests language which allow to filter information based on any given entities.
Example of such request is ```1(Machine Learning) AND 1(Deep | Convolutional)```, which would require "Machine learning" phrase to be present in a text,
along with either "Deep" or "Convolutional". This language allows to flexibly filter the corpus in order to analyze different entities such as persons, organisations, location and topics.

<div align="center">
    <img src=https://i.ibb.co/JktNXMt/68747470733a2f2f692e696d6775722e636f6d2f63645762456e6a2e6a706722.jpg">
    <p>Geo Dashboard</p>
</div>

# Practical uses
[Media Analytics](https://nlp.iict.kz/) can be applied in industrial tasks as :
1. Competitive to [ALEM MEDIA MONITORING](https://alem.kz/product-1/) service for:

    > Monitoring of media space (news websites, social networks, TV, etc.)

    > Reputation management, public opinion analysis, PR policies assessment and optimization

    > Decision making support

    > Configurable reporting and dashboards
    
    > NER requests filtering
    
    > KPI of marketing campaigns estimation, competitors comparative analysis, etc.

2. Service for searching most relevant bloggers/influencers for advertising in social networks: YouTube, Instagram, Facebook, etc.
Example of such service is [GetBlogger](https://getblogger.ru/)

    > Social network parsing, filtering by bloggers/authors popularity
    
    > Topic modelling of the corpora, obtaining topic embedding for separate publications and aggregating them to bloggers'/authors' topic embeddings
    
    > Creating a model which accepts textual information about business or product as an input, and outputs the most relevant bloggers/authors
