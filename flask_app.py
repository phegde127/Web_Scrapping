import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString  ## Create url to search
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()

            flipkart_html = bs(flipkartPage, "html.parser")
            models = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
            # models = flipkart_html.find_all("div", {"class": "bhgxx2 col-12-12"})
            list_reviews = []
            for i in range(7):
                try:

                    modellink = 'https://www.flipkart.com' + models[i].div.div.div.a['href']
                    modelopen = requests.get(modellink)
                    modelopen.encoding = 'utf-8'
                    model_html = bs(modelopen.text, "html.parser")
                    model_review_link = model_html.find('div', {'class': 'swINJg _3nrCtb'})
                    model_name = model_html.find_all('span', {'class': '_35KyD6'})[0].text.split('(')[0]

                    if model_review_link != None:
                        all_review_link = 'https://www.flipkart.com' + model_review_link.find_parent().get('href')
                        # print(all_review_link)
                        review_open = requests.get(all_review_link)
                        review_open_html = bs(review_open.content, "html.parser")
                        num_pages = review_open_html.find('div', {'class': '_2zg3yZ _3KSYCY'})
                        if num_pages != None:
                            s = num_pages.find('span').get_text().split()[-1]
                            pages = int(''.join(i for i in s if i.isdigit()))

                            for j in range(1, 2):  # variable 'pages' has the actual number of pages.
                                url = all_review_link + '&page=' + '{}'.format(j)
                                req_data = requests.get(url)
                                review_soup = bs(req_data.content, "html.parser")
                                # all_reviews = review_soup.find_all('div', {'class': '_3gijNv col-12-12'})
                                all_reviews = review_soup.find_all('div', {'class': '_1PBCrt'})
                                count = 1

                                for comment in all_reviews:
                                    count += 1
                                    try:
                                        name = comment.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                                        # name = comment.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                                    except:
                                        name = 'No name'

                                    try:
                                        rating = comment.div.div.div.div.text
                                    except:
                                        reating = 'No Rating'

                                    try:
                                        commenthead = comment.div.div.div.p.text
                                    except:
                                        commenthead = 'No Comment Heading'

                                    try:
                                        # custComment = comment.find_all('div', {'class': 'qwjRop'})[0].text
                                        custComment = comment.div.div.find_all('div', {'class': ''})[1].text
                                    except Exception as e:
                                        print("Exception while creating dictionary: ", e)

                                    mydict = {"Product": model_name, "Name": name, "Rating": rating,
                                              "CommentHead": commenthead,
                                              "Comment": custComment}

                                    list_reviews.append(mydict)


                        else:
                            reviews = model_html.find_all('div', {'class': '_3nrCtb'})
                            for comment in reviews:
                                try:
                                    name = comment.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                                    # name = comment.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                                except:
                                    name = 'No name'

                                try:
                                    rating = comment.div.div.div.div.text
                                except:
                                    reating = 'No Rating'

                                try:
                                    commenthead = comment.div.div.div.p.text
                                except:
                                    commenthead = 'No Comment Heading'

                                try:
                                    comtag = comment.div.div.find_all('div', {'class': ''})
                                    custComment = comtag[1].text
                                except Exception as e:
                                    print("Exception while creating dictionary: ", e)

                                mydict = {"Product": model_name, "Name": name, "Rating": rating,
                                          "CommentHead": commenthead,
                                          "Comment": custComment}

                                list_reviews.append(mydict)
                                # modellink

                    if model_review_link == None:
                        reviews = model_html.find_all('div', {'class': '_3nrCtb'})
                        for comment in reviews:
                            try:
                                name = comment.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                                # name = comment.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                            except:
                                name = 'No name'

                            try:
                                rating = comment.div.div.div.div.text
                            except:
                                reating = 'No Rating'

                            try:
                                commenthead = comment.div.div.div.p.text
                            except:
                                commenthead = 'No Comment Heading'

                            try:
                                comtag = comment.div.div.find_all('div', {'class': ''})
                                custComment = comtag[1].text
                            except Exception as e:
                                print("Exception while creating dictionary: ", e)

                            mydict = {"Product": model_name, "Name": name, "Rating": rating, "CommentHead": commenthead,
                                      "Comment": custComment}

                            list_reviews.append(mydict)

                except:
                    # print('Exception message as: ', e)
                    continue

            return render_template('results.html', reviews=list_reviews[0:(len(reviews) - 1)])

        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    #app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8001, debug=True)
