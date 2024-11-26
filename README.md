I am a software engineer. I am building a Python package to parse data from PDF statements.


I am using pdfplumber to extract the data, location boxes of data and all lines inside each pdf.

The user of the package will provide rules, inside a template, to extract data from a multi-page PDF statement.

- Templates will need coordinates as numbers : vertical lines, horizontal lines, header line. These are the boxes that define a column of data for each page.
- We provide rules to extract transaction data, based on pages eg. page 1 has certain rules, page 2 until penultimate page has different rules, last page has different rules. Ignore certain pages.
- Assume table has multi-line rows, user provides line delimiter in template (start of line, end of line). Delimiter can also be graphical horizontal line, use pdfplumber to find the coordinates of the line.
- Result is a JSON which follows a certain schema.
The end result from an extracted pdf will look like this JSON:

{
  "metadata": {
    "document_id": "1234567890",
    "parsed_at": "2024-01-01 12:00:00",
    "number_of_pages": 10
  },
  "pages": [
    {
      "forms": [
        {
          "sort_code": "20-00-00"
        },
        {
          "account_number": "1234567890"
        },
        {
          "customer_name": "John Doe"
        }
      ],
      "tables": [
        {
          "table_header": "Your Transactions",
          "data": [
            {
              "date": "2023-01-01",
              "description": "Payment Received",
              "amount": "150.00",
              "balance": "1200.00"
            },
            {
              "date": "2023-01-02",
              "description": "Monthly Subscription",
              "amount": "15.00",
              "balance": "1185.00"
            }
          ]
        }
      ]
    }
  ]
}


Please provide step by step instructions on how to build this package. Don't write any code, just provide the exact classes and methods that will be used. Be as detailed as possible without writing any code. Don't include any testing/CI/CD instructions. Just the classes and methods.