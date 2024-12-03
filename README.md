I am a software engineer. I am building a Python package to parse data from PDF statements.


I am using pdfplumber to extract the data, location boxes of data and all lines inside each pdf.

The user of the package will provide rules, inside a template, to extract data from a multi-page PDF statement.

- Templates will need bounding box coordinates. These are the boxes that define a column of data for each table.
- We provide rules to extract transaction data, based on pages eg. page 1 has certain rules, page 2 until penultimate page has different rules, last page has different rules. Ignore certain pages.
- Assume table has multi-line rows, user provides line delimiter in template (start of line, end of line). Delimiter can also be graphical horizontal line, use pdfplumber to find the coordinates of the line.

- Result is a JSON which follows a certain schema.
The end result from an extracted pdf will look like this JSON:



Use Parser to create a parser for table objects that is similar to Forms but uses horizontal line coordinates to split into form objects.

The horizontal line coordinates are detected by pdfplumber.

If no lines are provided, then the user must provide a delimiter which can  be used to split the table as well.


Focus on building this first, the thing that can split tables into form objects.

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


COORDINATES ARE DECIMAL COORDINATES STARTING FROM TOP LEFT CORNER OF THE IMAGE.

PDF extractor gets lines, text using pdf plumber, then also provides image and pixel hexcodes and can create original jpg and transformed jpg with lines. This is useful for debugging and inspecting the data. Top left corner of image is (0, 0). Bottom right corner is (1, 1).

Please provide step by step instructions on how to build this package. Don't write any code, just provide the exact classes and methods that will be used. Be as detailed as possible without writing any code. Don't include any testing/CI/CD instructions. Just the classes and methods.

Page numbers:

Use negative integers to specify pages relative to the last page:
-1: The last page.
-2: The second-to-last page.
-3: The third-to-last page, and so on.
Ranges:
Allow combinations of ranges and negative indices:
"2:-2": Pages 2 to the second-to-last page, inclusive for both.
"1:-1": First page to the last page (equivalent to "all").




NEED TO FIX HALIFAX AND LLOYDS