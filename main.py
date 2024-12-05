from experta import Rule, KnowledgeEngine, MATCH 
from controller import converFact_to_string, response
from facts import knowledge_base, BookFact
import math

# Expert system engine
class LibraryExpertSystem(KnowledgeEngine):
    def __init__(self, knowledge_base):
        super().__init__()
        self.knowledge_base = knowledge_base  # Reference to the knowledge base
        self.inferred_books = []
        self.alternatives = []
    
    # Rule: Match exact book parameters
    @Rule(
        BookFact(
            category=MATCH.category,
            author=MATCH.author,
            target_audience=MATCH.target_audience,
            language=MATCH.language,
            book_type=MATCH.book_type,
            keywords=MATCH.keywords,
            rating=MATCH.rating
        ),
        salience=10,  # High priority for exact matches
    )
    def exact_match(self, category, author, target_audience, language, book_type, keywords, rating):
        self.inferred_books = [
            converFact_to_string(book) for book in self.knowledge_base if 
            category is not None and book["category"].lower() == category.lower() and 
            author is not None and book["author"].lower() == author.lower() and 
            target_audience is not None and book["target_audience"].lower() == target_audience.lower() and 
            language is not None and book["language"].lower() == language.lower() and 
            book_type is not None and book["book_type"].lower() == book_type.lower() and 
            # book["keywords"].intersection(keywords) and keywords is not None and
            # len(book["keywords"].intersection(keywords)) ==len(keywords) and keywords is not None and
            keywords is not None and len({i.lower() for i in book["keywords"]}.intersection({j.lower() for j in keywords})) ==len(keywords) and len(book["keywords"])==len(keywords) and
            rating is not None and book["rating"] >= rating - 0.5 and book["rating"] <= rating + 0.5 
        ]
        
        if self.inferred_books:
            print("\nExact Matches Found:")
            response.update({"response_messege":"Based on the preferences you shared—category, author, target audience, language, book type, keywords, and rating—I can recommend some books that match exactly what you're looking for",
                             "response_data":self.inferred_books})
            print(response)

    # Rule: Suggest alternatives based on partial matches
    @Rule(
        BookFact(
            keywords=MATCH.keywords,
            category=MATCH.category,
            author=MATCH.author,
            target_audience=MATCH.target_audience,
            language=MATCH.language,
            rating=MATCH.rating,
            book_type=MATCH.book_type
        ),
        salience=7,  # Medium priority for partial matches
    )
    def suggest_alternatives(self, keywords, category,author, target_audience, language, rating,book_type):
        self.alternatives = []
        null_values_list=[]
                                            
        if not self.inferred_books:
            
         if not category or category in ["no idea","anything","any","no preference","no specific"]:
             null_values_list.append("category")
         if not author or author in ["no idea","anything","any","no preference","no specific"]:
             null_values_list.append("author")
         if not target_audience or target_audience in ["no idea","anything","any","no preference","no specific"]:
             null_values_list.append("target_audience")
         if not language or language in ["no idea","anything","any","no preference","no specific"]:
             null_values_list.append("language") 
         if not rating or rating in ["no idea","anything","any","no preference","no specific"]:
             null_values_list.append("rating")
         if not book_type:
             null_values_list.append("book_type")
        #  if not keywords or keywords in ["no idea","anything","any","no preference","no specific"]:
         if not keywords or any(keyword in ["no idea", "anything", "any", "no preference", "no specific"] for keyword in keywords):

             null_values_list.append("keywords")
             
         totalMarks=len(keywords)+15
         for book in self.knowledge_base:
            relevance_score = 0
            
            # Calculate relevance score
            
            # Match keywords
            relevance_score += len(book["keywords"].intersection(keywords))
            
            # Match rating with tolerance
            if book["rating"] >= rating - 0.5 and book["rating"] <= rating + 0.5:
                relevance_score += 1
            
            # Match category, target audience, and language
            if category is not None and book["category"].lower() == category.lower():
                relevance_score += 6
                
            if target_audience is not None and book["target_audience"].lower() == target_audience.lower():
                relevance_score += 1
            if language is not None and book["language"].lower() == language.lower():
                relevance_score += 1
            if author is not None and book["author"].lower() == author.lower():
                relevance_score += 4    
            if book_type is not None and book["book_type"].lower() == book_type.lower():
                relevance_score += 2    
                
           
            # Add book to alternatives if relevance score > 0
            if relevance_score > 0:
             score=math.floor((relevance_score/totalMarks)*100)
             self.alternatives.append((converFact_to_string(book), score))
        
            # Sort by relevance score in descending order
         self.alternatives.sort(key=lambda x: x[1], reverse=True)

            # If no exact matches, suggest top alternatives
            # if not self.inferred_books:
        
         if null_values_list:
            String_value =" , ".join(map(str, null_values_list))
            print(String_value)
            if  not self.alternatives:
                response.update({"response_messege":"You don't tell me any thing.So you can choose any book you want",
                               "response_data":self.alternatives})
            else: 
                num_of_books=math.ceil(len(self.alternatives)/2)   
                response.update({"response_messege":f"Although you didn’t mention specifics about {String_value}, I’ve taken that into account and found some alternative recommendations for you. Here are the books I think you might like : ",
                               "response_data":self.alternatives[:num_of_books]})
         else:
            num_of_books=math.ceil(len(self.alternatives)/2)  
            _,percentage=self.alternatives[0]
            if percentage==100:
                response.update({"response_messege":"I can recommend you several books that closely match your preferences, including some that are highly aligned with your interests, and even a few that match exactly",
                               "response_data":self.alternatives[:num_of_books]})
            else:     
                response.update({"response_messege":"I looked through our collection, but unfortunately, I couldn’t find any books that match all of your exact preferences. However, I did find some books that are quite close to what you’re looking for. I hope these might still interest you!.Here are my recommendations: ",
                               "response_data":self.alternatives[:num_of_books]})   
              
         print(response)
        # print(null_values_list)
        
        # print("\nNo exact matches found. Alternative recommendations:")
        # for alt, relevance in self.alternatives[:4]:  # Limit to top 3 recommendations
        #     print(f"{alt} (Relevance Score: {relevance})")
                
    # Rule: Find authors with similar styles
    
    @Rule(
        BookFact(
            category=MATCH.category,
            keywords=MATCH.keywords,
            author=MATCH.author
        ),
        salience=6,
    )
    def find_similar_authors(self, category, keywords, author):
        self.similar_authors = [
            (book.author, len(book.keywords.intersection(keywords)))
            for book in self.knowledge_base
            if book.category == category and book.author != author
        ]
        self.similar_authors.sort(key=lambda x: x[1], reverse=True)  # Sort by keyword overlap
        print("\nAuthors with Similar Styles:")
        for author, relevance in self.similar_authors[:3]:  # Limit to top 3 authors
            print(f"Author: {author} (Relevance Score: {relevance})")            

    # Rule: Backward chaining to find book category
    @Rule(BookFact(title=MATCH.title), salience=8)
    def backward_chaining_category(self, title):
        matching_books = [book for book in self.knowledge_base if book["title"].lower() == title.lower()]
        if matching_books:
            book = matching_books[0]
            print(f"\nBackward Chaining Result for '{title}':")
            print(f"Category: {book['category']}")
            print(converFact_to_string(book))
        else:
            print(f"No book found with the title '{title}'.")


# Instantiate and populate the expert system
engine = LibraryExpertSystem(knowledge_base)

# Start forward chaining with user inputs
# user_params = BookFact(
#     category="Technology",
#     author="Andrew Ng",
#     keywords={"AI", "machine learning"},
#     rating=4.5,
#     target_audience="Teens",
#     language="English",
#     book_type="Paperback"
# )

# user_params = BookFact(
#     category="Technology",
#     author="",
#     keywords={"machine learning"},
#     rating=0,
#     target_audience="",
#     language="",
#     book_type=""
# )

user_params = BookFact(
    category="Technology",
    author="",
    keywords={},
    rating=0,
    target_audience="",
    language="",
    book_type=""
)

print("\n--- Forward Chaining ---")
engine.reset()
engine.declare(user_params)
engine.run()

# Backward chaining for a book title
# print("\n--- Backward Chaining ---")
# engine.reset()
# engine.declare(BookFact(title="AI for Everyone"))
# engine.run()
