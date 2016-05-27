#Zhihu-Analytics-Service
Zhihu is a Chinese question-and-answer website where questions are created, answered, edited and organized by the community of its users. This full stack web service is developed in python for crawling large data of users and questions-answers information, as well as data storage, analysis, and visualization.

#Crawling
A multi-threading crawling system that supports proxies crawling and validation, dynamic user-agents and proxies for anti-anti-crawling and crawling frequency control. Crawlable contents include user image, user thanks/agrees, user followers/followees, user questions/answers, user timelines, question topics/text, answers text/agrees

#Storage
Supports both on-disk file (in JSON format) storage type and database storage type. MongoDB is used as the database backend for easier scaling in future development of distributed web service

#Analyzing
Used Jieba API for Chinese text segmentation (using max likelihood route finding on sentence DAG for loaded dictionary words and HMM for unloaded words) and TF-IDF for keywords extraction. Analysis include topic clustering, users/questions recommendation (BOW similarity based), popularity analysis (PageRank based), quality analysis and social graph analysis. More advanced analysis includes sentiment analysis using SnowNLP API.

#Web and Visualization
A full stack service is built to provide interactive experience on all crawled and analyzed data. Flask framework is used for bridging backend data and frontend services. Boostrap is used to easily build frontend HTML/CSS/JavaScript frames. Dynamic visualization is realized using d3.js.

#APIs
APIs for crawling, keywords extraction, various analysis and recommendation can be directly applied and embedded for developing other applications. Detailed info on APIs can be found in each module.

#Requirement
*Database: MongoDB and pymongo
*Web packages: requests, bs4(BeautifulSoup), flask
*NLP packages: Jieba, SnowNLP
*other: pillow
