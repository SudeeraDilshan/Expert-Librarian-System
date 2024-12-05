
def converFact_to_string(fact):
    return {"title":fact['title'],
            "category":fact['category'],
            "author":fact['author'],
            "target_audience":fact['target_audience'],
            "language":fact['language'],
            "book_type":fact['book_type'],
            "rating":fact['rating'],
            "keywords":fact['keywords']}
    
response={"response_messege":"",
          "response_data":[]
          }    

def get_book(book:dict):
    return f"""
          Title:{book.get('title', 'Unknown Title')}\n
          Author:{book.get('author', 'Unknown Author')}\n
          Category:{book.get('category', 'Unknown Category')}\n
          Rating: {book.get('rating', 'N/A')}\n
          Target Audience: {book.get('target_audience', 'N/A')}\n
          Language: {book.get('language', 'Unknown Language')}\n
           Book Type: {book.get('book_type', 'N/A')}\n
           Keywords: {', '.join(book.get('keywords', []))}
          
                """
