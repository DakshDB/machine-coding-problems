# library Management 

- Member 
    - id
    - name
    - email
- Book
    - title
    - isbn
    - author
- BookCopy
    - isbn
    - barcode
- Loan
    - id 
    - barcode
    - loan_date

Operation 
- borrow_book(member_id, isbn) -> Loan
- return_book(barcode) -> fine
- get_available_copies(isbn) -> where
- get_loans_by_member(member_id) -> Loans

Constant 
- Loan Period - 14 Days 
- Fine - 5 per day
- Max Fine - 500
- Max Loan Per Member - 5
- Max Due Fine For New Loan - 100

